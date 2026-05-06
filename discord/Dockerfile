FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
COPY discord_bot.mjs .
COPY discord_utils.mjs .
EXPOSE 3000
CMD ["node", "discord_bot.mjs"]