FROM node:20-bookworm-slim

WORKDIR /app

# Copy only package.json to force a complete re-resolution of Linux-specific binaries
COPY package.json ./
RUN npm install
COPY . .

# Expose port and run dev server
EXPOSE 3000
ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["npm", "run", "dev"]
