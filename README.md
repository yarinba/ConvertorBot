# Currency Converter Bot

This project implements a currency converter program using python3 and Telegram Bot API.


## Installation

Clone this repo and use [pip](https://pip.pypa.io/en/stable/) to install requirements -

bash
pip install -r requirements.txt


Create a new folder named "res" and make 3 json files inside it

bash
'res/Currency.json'
'res/settings.json'
'res/UserChoice.json'

Get a bot "Token" from [BotFather](https://core.telegram.org/bots#:~:text=for%20existing%20ones.-,Creating%20a%20new%20bot,mentions%20and%20t.me%20links.) and add it to 'res/settings.json'
bash
{
    "Token":"YourTokenHere"
}

Once your bot token is in place you can run the project.

## Usage
All usage is inside your Telegram-Bot conversation,
the bot will respond with interactive buttons to handle all flows.



## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
