const GCLIENT_ID = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.apps.googleusercontent.com';
const GCLIENT_SECRET = 'xxxxxxxxxxxxxxxxxxxxxxxx';
const GCLIENT_REFRESH = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx';
const TELEGRAM_SECRET = '9999999999:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx';

const LABELS = {
    'Label_9999999999999999998': ['@canal_edisciplinas_2021', '9999999999'],
    'Label_9999999999999999999': ['9999999999'],
};
const ADMINS = ['9999999999']

const OAUTH_ENDPOINT = 'https://oauth2.googleapis.com/token?grant_type=refresh_token&client_secret=' +
    GCLIENT_SECRET + "&refresh_token=" + GCLIENT_REFRESH + "&client_id=" + GCLIENT_ID;
const GMAIL_ENDPOINT = 'https://gmail.googleapis.com/gmail/v1/users/me/messages';
const TELEGRAM_ENDPOINT = 'https://api.telegram.org/bot' + TELEGRAM_SECRET + '/sendMessage';

let gmail_header;
let oauth_access_token;

async function get_access_token() {
    const header = { 'content-type': 'application/x-www-form-urlencoded' };
    const request = await fetch(OAUTH_ENDPOINT, { method: 'POST', headers: header });
    const response = await request.json();
    if (response['access_token'] == null) throw "get_access_token(): "+JSON.stringify(response);
    return response['access_token'];
}


async function list_message_ids(label) {
    const label_string = '?labelIds=UNREAD&labelIds=' + label;
    const request = await fetch(GMAIL_ENDPOINT + label_string, { method: 'GET', headers: gmail_header });
    const response = await request.json();

    const id_list = []
    if (response['resultSizeEstimate'] == 0) return id_list;
    for (const message of response['messages']) id_list.push(message['id']);
    id_list.reverse();
    return id_list;
}


async function get_message(msg_id) {
    const request = await fetch(GMAIL_ENDPOINT + '/' + msg_id + '?format=full', { method: 'GET', headers: gmail_header });
    const response = await request.json();

    let data = response['payload']['parts'][0]['body']['data'];
    data = data.replace(/_/g, '/').replace(/-/g, '+');
    data = decodeURIComponent(atob(data).split('').map(function (c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));

    const pattern = '---------------------------------------------------------------------';
    data = data.split(pattern);
    data = data[0].substring(0, 2) + '#' + data[0].substring(2, 9) + ' ' + data[0].substring(9)
        + pattern + data[1] + pattern;

    if (data.length > 4000) return data.substring(0, 4000)+"........";
    return data;
}


async function mark_as_read(msg_id) {
    const changes = '{"removeLabelIds":["UNREAD"]}';
    const request = await fetch(GMAIL_ENDPOINT + '/' + msg_id + '/modify', { method: 'POST', body: changes, headers: gmail_header });
    const response = await request.json();
}


async function telegram_send(message, chat_list) {
    let errors = [];
    for (const chat_id of chat_list) {
        const header = { 'Content-Type': 'application/json' }
        const data = JSON.stringify({ 'chat_id': chat_id, 'text': message });
        const request = await fetch(TELEGRAM_ENDPOINT, { method: 'POST', body: data, headers: header });
        const response = await request.json();
        if (response['ok'] == false) errors.push(response['description'] + ` (${chat_id})`);
    }
    if (errors.length != 0) throw "telegram_send(): "+JSON.stringify(errors);
}


async function handleRequest(request) {
    try {
        oauth_access_token = await get_access_token();
    }
    catch(e) {
        await telegram_send(JSON.stringify(e), ADMINS);
        return new Response("oauth_access_token error", { status: 299 });
    }

    gmail_header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + oauth_access_token,
    };

    for (const label of Object.keys(LABELS)) {
        const message_list = await list_message_ids(label);
        for (const msg_id of message_list) {
            try {
                const message = await get_message(msg_id);
                await telegram_send(message, LABELS[label]);
                await mark_as_read(msg_id);
            }
            catch(e) {
                await telegram_send(JSON.stringify(e), ADMINS);
            }
        }
    }
    return new Response("everything ok :)", { status: 200 });
}

// addEventListener('fetch', event => {
//     event.respondWith(handleRequest(event.request));
// })

addEventListener('scheduled', event => {
    event.waitUntil(handleRequest(event.scheduledTime));
})
