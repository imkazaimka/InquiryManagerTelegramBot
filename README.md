# Telegram Bot

This is a Telegram bot built using the [Aiogram](https://docs.aiogram.dev/en/latest/) framework. The bot is designed to streamline user interactions and automate tasks efficiently.

## Features
- User-friendly interface.
- Secure handling of sensitive information with `.env`.
- Modular and scalable structure.
- Persistent deployment using `tmux` or `systemd`.

---

## Table of Contents
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Bot](#running-the-bot)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [Support](#support)

---

## Installation

### Requirements
- Python 3.8 or higher
- A Telegram bot token from [BotFather](https://t.me/BotFather)

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/<your_username>/<your_repo>.git
   cd <your_repo>
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Configuration

### Setting Up Environment Variables
1. Create a `.env` file in the project root:
   ```bash
   touch .env
   ```

2. Add the required environment variables:
   ```plaintext
   BOT_TOKEN=your_bot_token_here
   DATABASE_URL=your_database_url_here
   ```

3. Refer to the `.env.example` file for the structure:
   ```plaintext
   BOT_TOKEN=your_bot_token_here
   DATABASE_URL=your_database_url_here
   ```

---

## Running the Bot

### Locally
1. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

2. Run the bot:
   ```bash
   python run.py
   ```

3. Exit the virtual environment when done:
   ```bash
   deactivate
   ```

### Persistent Deployment
For persistent deployment on a server, you can use:
- **`tmux`**: Run the bot in a detached session.
- **`systemd`**: Automate bot restarts and ensure uptime.

Refer to the [Deployment](#deployment) section for details.

---

## Deployment

### Using `tmux`
1. Start a `tmux` session:
   ```bash
   tmux new -s bot_session
   ```

2. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

3. Run the bot:
   ```bash
   python run.py
   ```

4. Detach the session:
   Press `Ctrl + B`, then `D`.

### Using `systemd`
1. Create a `systemd` service file:
   ```bash
   sudo nano /etc/systemd/system/bot.service
   ```

2. Add the following content:
   ```ini
   [Unit]
   Description=Telegram Bot
   After=network.target

   [Service]
   User=root
   WorkingDirectory=/path/to/project
   ExecStart=/path/to/project/venv/bin/python /path/to/project/run.py
   EnvironmentFile=/path/to/project/.env
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. Save the file and reload `systemd`:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable bot
   sudo systemctl start bot
   ```

4. Check the status:
   ```bash
   sudo systemctl status bot
   ```

---

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add a meaningful commit message"
   ```
4. Push to your fork and submit a pull request.

---

## Support
For issues or questions, open an issue on the [GitHub repository](https://github.com/<your_username>/<your_repo>).

Happy coding!

