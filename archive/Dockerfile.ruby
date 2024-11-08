# # Dockerfile.ruby
# FROM ruby:3.0

# # Install system dependencies
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     libffi-dev \
#     && rm -rf /var/lib/apt/lists/*

# # Install bundler and jekyll
# RUN gem install bundler jekyll

# # Set the working directory
# WORKDIR /app

# # Copy dependency files
# COPY ./src/Gemfile ./

# # Install Ruby dependencies
# RUN bundle install

# # Copy the application code
# COPY ./src/ ./

# # Copy supervisor configuration
# COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# # Expose ports
# EXPOSE 4002

# # Command to start Jekyll application
# CMD ["bundle", "exec", "jekyll", "serve", "--config", "_config.yml,_config_dev.yml", "--host", "0.0.0.0", "--port", "4002"]