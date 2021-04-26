
# Quack3Bot

quack quack. quack.

## Contents
 - [Introduction](#introduction)
 -  [Setup](#setup)
	 - [1. Telegram](#1-telegram)
	 - [2. Gmail Labels](#2-gmail-labels)
	 -  [3. Google OAuth Credentials](#3-google-oauth-credentials)
	 - [4. Serverless Script](#4-serverless-script)


## Introduction

Quack3Bot is a bot that will frequently check for unread emails with a specific label and send it by Telegram to you, some channel or any other predefined user. To make the it work you will need to create a new bot, create credentials to allow access to your emails, generate the script behind the bot and deploy the script in a digital platform.  

## Setup

### 1. Telegram

**Create a bot with [@BotFather](https://t.me/botfather).** Send the message "`/newbot`"  to the Telegram's official bot manager called [BotFather](https://t.me/botfather) and create your new bot . You should receive a authorization token at the end of the process, keep it safe.

### 2. Gmail Labels

**Create filters that will apply some label to the wanted emails.**  You can follow the [official guide to create a filter](https://support.google.com/mail/answer/6579#zippy=,create-a-filter). To create a good filter for the forum notification emails, you can use this example:

 - From: `@edisciplinas.usp.br OR list:(@edisciplinas.usp.br)`
 - Has the words: `fóruns`
 - Doesn't have**: `"Este e-mail é a cópia de uma mensagem que foi enviada para você em 'e-Disciplinas'."`
 
 ** Caution if you are sending these messages to a public channel because sensitive data can be send to you by the same email addresses. The example shows a piece of text presented in notifications of received personal messages from the Moodle that always need to be filtered out.

### 3. Google OAuth Credentials

**Create new credentials with `http://localhost:8000` as a *Authorized redirect URI* and get the *Client ID* and *Client secret* from it.** This part can be confusing because of the the quantity of buttons... You can follow this [guide created for the AdWords documentation](https://developers.google.com/adwords/api/docs/guides/authentication#webapp) and add the url `http://localhost:8000` at **Authorized redirect URIs** in step 5.

Notes:
- Make sure you copied `http://localhost:8000` exactly as it is.
 - At the *OAuth consent screen* you can be asked about the user type among other things. Just fill with default values and select *Internal* user type. It shoudn't make any difference if you are not sharing the created project with other accounts.
 - OAuth Credentials are only one step from accessing all of your Google account, please keep it safe. If anything happens, reset your secret or delete the compromised credential immediately.

 

### 4. Serverless Script

**Generate your serverless script using the [wizard.py](https://github.com/wilwxk/quack3bot/blob/main/wizard.py) script and deploy it to the Cloudflare Workers platform.** 

4.1 - Download/save the [wizard.py script](http://raw.githubusercontent.com/wilwxk/quack3bot/main/quack3bot.js), run it with `python wizard.py` and follow the instructions.

4.2 - With the copied script in your clipboard  [create an account at Cloudflare](https://dash.cloudflare.com/sign-up/workers), go to the Workers dashboard and create a [new Worker](https://dash.cloudflare.com/?account=workers). Delete the existing example code, paste your generated script and click in *Save and Deploy*.

4.3 - Go to the created Worker settings, on the *Triggers* tab click in *Add Cron Trigger*. You can change the expression to whatever you want, if the expression is `*/5 * * * *` for example, the bot will check for new emails every 5 minutes. Remember to save it. There is a nice [screenshot in the docs](https://developers.cloudflare.com/workers/platform/cron-triggers#adding-cron-triggers) if you are lost.

4.4 - You are done :)
