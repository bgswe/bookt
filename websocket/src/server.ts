import WebSocket from 'ws'

import logger from './logger'

type WebsocketMessage = ArrayBuffer | Blob | Buffer | Buffer[]

class BooktWebsocket {
  wss: WebSocket.Server = null
  open = false

  constructor(port: number) {
    this.wss = new WebSocket.Server({ port })

    this.wss.on('connection', (wss: WebSocket) => {
      wss.on('message', this.handleMessage)
      wss.on('close', this.close)
    })
  }

  handleMessage(message: WebsocketMessage): void {
    logger.info('handle message')
    logger.info(message)
  }

  close(): void {
    logger.info('client connection closed')
  }
}

new BooktWebsocket(8081)
