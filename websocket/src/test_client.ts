import WebSocket from 'ws'

import logger from './logger'

const ws = new WebSocket('ws://localhost:8081')

class CommandResult {}

ws.on('open', () => {
    logger.info('connected to server')

    ws.send('50f8ccdc-97b3-4bb7-ae6b-8a75ea5cabfa')
})

ws.on('message', (message: string) => {
    logger.info(`received message from server: ${message}`)
})

ws.on('close', () => {
    logger.info('disconnected from server')
})
