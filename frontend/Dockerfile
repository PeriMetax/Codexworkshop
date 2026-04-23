FROM node:22-alpine
WORKDIR /app
COPY package.json tsconfig.json next.config.ts next-env.d.ts ./
COPY src ./src
RUN npm install
CMD ["npm", "run", "dev", "--", "-p", "3000", "-H", "0.0.0.0"]
