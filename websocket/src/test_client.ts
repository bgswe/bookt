import WebSocket from "ws";

import logger from "./logger"

const ws = new WebSocket("ws://localhost:8081");

ws.on("open", () => {
  logger.info("connected to server");

  ws.send("Hello, server!");
});

ws.on("message", (message: string) => {
  logger.info(`received message from server: ${message}`);
});

ws.on("close", () => {
  logger.info("disconnected from server");
});
