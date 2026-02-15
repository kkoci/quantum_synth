FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy project
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Start with host flag to bind to 0.0.0.0
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
