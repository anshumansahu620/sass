FROM node:20-alpine

WORKDIR /app

# Copy dependency manifests
COPY package*.json ./

# Install production dependencies
RUN npm install --omit=dev

# Copy application source code
COPY . .

# Expose the default WebSocket port
EXPOSE 8080

# Environment defaults
ENV PORT=8080 \
    NODE_ENV=production

# Use non-root node user
USER node

# Start the WebSocket server
CMD ["node", "index.js"]
