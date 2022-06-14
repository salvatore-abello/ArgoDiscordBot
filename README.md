# ArgoDiscordBot
A bot that interfaces Argo Scuola Next with Discord.

### Features
- Check the announcements and reminders every two minutes, it is faster than the official Argo Scuola Next application.
- Sends homework for the next day at a specific time (14:00).
- Sends reminders via text.
- He can send the homework via text and also via HTML table. Here's an example of how the bot sends the table with the homework: 
<img width="505" alt="image" src="https://user-images.githubusercontent.com/107145304/173253373-d3219acd-ab64-4f3b-a4bd-3d2c232b9fe8.png">

## Usage
### To receive homework
- `!compiti domani` `!compiti oggi` `!compiti dopodomani`: The bot sends the homework for tomorrow/today/the day after tomorrow
- `!compiti 30/04/22`: The bot sends the homework for 30th April
- `!compiti`: The bot sends the homework for tomorrow
- `!compiti lunedì` `!compiti lun` The bot sends the homework for the next Monday
- `!compiti lunedì i`, The bot sends the homework via image

Supported date format:
- `dd-mm-yy` Eg. `30-05-22`, `30 05 22`, `30/05/22`
- `YYYY-mm-dd` Eg. `2022-05-30`, `2022 05 30`, `2022/05/30`
- `yy-mm-dd` Eg. `22-05-30`, `22 05 30`, `22/05/30`
- `dd-mm-YYYY` Eg. `30-05-2022`, `30 05 2022`, `30/05/2022`

There are other supported separators, but these are the most common ones.


### To receive reminders
`!promemoria`

------------

## Setup
First of all, install the dependencies with `pip install -r requirements.txt`.
Next, change the values of `DISCORD_TOKEN`, `PASSWORD`, `USERNAME` and `SCHOOL_CODE` in `main.py`. These ones must be strings.

Finally, change the values of `self.server_id`, `self.compiti_channel_id`, `self.comunicazioni_channel_id`. These ones must be integers.

**This bot uses the [Argo Scuola Next API](https://github.com/salvatore-abello/argofamiglia "Argo Scuola Next API").**

## DISCLAIMER
Use this bot at your own risk, as it violates the terms of the services of Argo Scuola Next.

```The authentication token and the restful services invoked through it, can only be used by the "DidUP - Famiglia" application of Argo Software SRL for the provision of its services or by saas suppliers and related applications specifically pre-authorized, in compliance with current legislation in manner of protection of personal data and the measures required by the AgID for the SaaS applications of the PA.```

```Il token di autenticazione e i servizi restful invocati mediante esso, possono essere utilizzati solo dall'applicazione "DidUP - Famiglia" della Argo Software SRL per l’erogazione dei propri servizi o da fornitori saas e relative applicazioni appositamente preautorizzate, in conformità alla vigente normativa in maniera di protezione dei dati personali ed alle misure richieste dall'AgID per gli applicativi SaaS delle PA.```
