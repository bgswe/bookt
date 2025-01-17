import { Consumer, EachMessageHandler, Kafka } from 'kafkajs'
import WebSocket, { RawData } from 'ws'

import logger from './logger'

interface CommandResult {
    created: string // YYYY-MM-DD HH:MM:SS
    message_id: string // uuid
    command_id: string // uuid
    command_type: string
    status: 'success' | 'failure'
}

interface CommandResultSubscriptionService {
    publishResult(commandResult: CommandResult): void
}

type Function = (...args: unknown[]) => unknown

interface CommandResultConsumer {
    consume_stream(streamId: string, messageHandler: Function): void
}

class BooktCommandResultStreamingApp {
    constructor(
        commandResultStreamId: string,
        command_results_subscription_service: CommandResultSubscriptionService,
        command_result_consumer: CommandResultConsumer,
    ) {
        command_result_consumer.consume_stream(
            commandResultStreamId,
            async ({ message }) => {
                const messageJSONStr = message.value.toString()
                const messageJSON = JSON.parse(messageJSONStr)
                command_results_subscription_service.publishResult(messageJSON)
            },
        )
    }
}

interface KafkaConsumerConfig {
    clientId: string
    brokers: string[]
    groupId?: string
}

class KafkaConsumer {
    kafka: Kafka
    consumer: Consumer

    constructor(config: KafkaConsumerConfig) {
        this.kafka = new Kafka({
            clientId: config.clientId,
            brokers: config.brokers,
        })
        this.consumer = this.kafka.consumer({
            groupId: config.groupId || config.clientId,
        })
    }

    async consume_stream(streamId: string, messageHandler: EachMessageHandler) {
        await this.consumer.connect()
        await this.consumer.subscribe({ topic: streamId, fromBeginning: true })
        await this.consumer.run({ eachMessage: messageHandler })
    }
}

class WebSocketCommandResultSubscriptionService {
    wss: WebSocket.Server
    command_result_subscriptions: Record<string, WebSocket[]> = {}

    constructor(port: number) {
        this.wss = new WebSocket.Server({ port })
        this.wss.on('connection', (ws: WebSocket) => {
            ws.on('message', (...args) => this.#handleMessage(ws, ...args))
            ws.on('close', this.#close)
        })
    }

    publishResult(commandResult: CommandResult): void {
        const { command_id: commandId } = commandResult
        if (commandId in this.command_result_subscriptions) {
            const jsonStr = JSON.stringify(commandResult)
            this.command_result_subscriptions[commandId].forEach((ws) =>
                ws.send(jsonStr),
            )

            logger.info(`found subscriptions for commandId: ${commandId}`)
        } else {
            logger.info(`no subscriptions found for commandId: ${commandId}`)
        }
    }

    #handleMessage(
        ws: WebSocket,
        rawMessage: RawData,
        isBinary: boolean,
    ): void {
        if (isBinary)
            throw Error("this websocket doesn't accept binary messages")

        if (rawMessage instanceof Array) {
            // NOTE??: I believe this is multiple messages?
            rawMessage.forEach(() => {})
        } else {
            const decoder = new TextDecoder()
            const message = decoder.decode(rawMessage)

            logger.info(`received message: ${message}`)

            // the current expectation is the message is the command ID to subscribe to
            if (this.command_result_subscriptions[message])
                this.command_result_subscriptions[message].push(ws)
            else this.command_result_subscriptions[message] = [ws]
        }
    }

    #close(): void {
        logger.info('client connection closed')
    }
}

new BooktCommandResultStreamingApp(
    'command_results',
    new WebSocketCommandResultSubscriptionService(8081),
    new KafkaConsumer({
        clientId: 'bookt-websocket',
        brokers: ['localhost:29092'],
    }),
)
