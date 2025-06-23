# Multi-stage build for Flutter web
FROM debian:latest AS build-env

# Install Flutter dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    unzip \
    xz-utils \
    zip \
    libglu1-mesa \
    && rm -rf /var/lib/apt/lists/*

# Clone Flutter
RUN git clone https://github.com/flutter/flutter.git /flutter
ENV PATH="/flutter/bin:${PATH}"

# Enable web
RUN flutter channel stable
RUN flutter upgrade
RUN flutter config --enable-web

# Create non-root user
RUN useradd -m -u 1000 flutteruser

# Copy app files
WORKDIR /app
COPY . .

# Change ownership to flutteruser
RUN chown -R flutteruser:flutteruser /app

# Switch to flutteruser
USER flutteruser

# Get app dependencies
RUN flutter pub get

# Build the app for the web
RUN flutter build web --release

# Production stage
FROM nginx:alpine

# Copy built app from previous stage
COPY --from=build-env /app/build/web /usr/share/nginx/html

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
