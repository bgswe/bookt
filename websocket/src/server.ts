import WebSocket from "ws";

import logger from "./logger"

const wss = new WebSocket.Server({ port: 8081 })

wss.on('connection', (ws: WebSocket) => {
    logger.info("new client connected")

    ws.on('message', (message: string) => {
        logger.info(`received message: ${message}`)

        ws.send(`server received your message: ${message}`)
    })

    ws.on('close', () => {
        logger.info("client disconnected")
    })
});
