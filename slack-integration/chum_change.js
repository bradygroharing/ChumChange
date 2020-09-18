// Import express and request modules
var express = require('express');
var request = require('request');
// var sys = require('sys')
// var exec = require('child_process').exec;
var IncomingWebhook = require('@slack/client').IncomingWebhook;
const { createEventAdapter } = require('@slack/events-api');
const slackSigningSecret = process.env.SLACK_SIGNING_SECRET;
const slackEvents = createEventAdapter(slackSigningSecret);

// Store our app's ID and Secret. These we got from Step 1.
// For this tutorial, we'll keep your API credentials right here. But for an actual app, you'll want to  store them securely in environment variables. 
var clientId = '46378622003.176720392310';
var clientSecret = 'f253bebb75ab7e9f01d90fe5a14b2be6';
// var token = process.env.SLACK_API_TOKEN || 'xoxp-46378622003-46427242645-178396187058-d516fa1aba91a692ffc4e431c6165a68'; //see section above on sensitive data
var url = process.env.SLACK_WEBHOOK_URL || 'https://hooks.slack.com/services/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'; //see section above on sensitive data 


// Instantiates Express and assigns our app variable to it
var app = express();
// var web = new WebClient(token);
var webhook = new IncomingWebhook(url);


// Again, we define a port we want to listen to
const PORT=6969;

// Lets start our server
app.listen(PORT, function () {
    //Callback triggered when server is successfully listening. Hurray!
    console.log("Chum Change is listening on port " + PORT);
});


// This route handles GET requests to our root ngrok address and responds with the same "Ngrok is working message" we used before
app.get('/', function(req, res) {
    res.send('server is working! Path Hit: ' + req.url);
});

// This route handles get request to a /oauth endpoint. We'll use this endpoint for handling the logic of the Slack oAuth process behind our app.
app.get('/oauth', function(req, res) {
    // When a user authorizes an app, a code query parameter is passed on the oAuth endpoint. If that code is not there, we respond with an error message
    if (!req.query.code) {
        res.status(500);
        res.send({"Error": "Looks like we're not getting code."});
        console.log("Looks like we're not getting code.");
    } else {
        // If it's there...
        // We'll do a GET call to Slack's `oauth.access` endpoint, passing our app's client ID, client secret, and the code we just got as query parameters.
        request({
            url: 'https://slack.com/api/oauth.access', //URL to hit
            qs: {code: req.query.code, client_id: clientId, client_secret: clientSecret}, //Query string data
            method: 'GET', //Specify the method

        }, function (error, response, body) {
            if (error) {
                console.log(error + "This is my own error line 47");
            } else {
                res.json(body);
            }
        })
    }
});

//This route will take in an amount and a recipient and send a curl command to the ChumChange blockchain
//We'll need to figure out how to get the person who wrote the command and use that as the sender
app.post('/pay', function(req, res) {
    res.send('Your server is up and running!');
});

//This route will take in an a user and send a curl command to the ChumChange blockchain
//We'll need to figure out how to get the person who wrote the command and use that as the user
app.post('/balance', function(req, res) {
    res.send('Your server is up and running!');

});

app.post('/event', function(req, res) {
    console.log(req.event);
    let challenge = req.body.challenge;
    res.send(challenge);
});

slackEvents.on('message', (event) => {
    console.log(`Received a message event: user ${event.user} in channel ${event.channel} says ${event.text}`);
});
   
(async () => {
const server = await slackEvents.start(port);
console.log(`Listening for events on ${server.address().port}`);
})();



// Route the endpoint that our slash command will point to and send back a simple response to indicate that ngrok is working
// app.post('/command', function(req, res) {
//     res.send('Your server is up and running!');
    
//     // child = exec("sh script.sh", function (error, stdout, stderr) {
//     //     if(stdout != '') {
//     //      console.log(stdout);
//     //     }
//     //     else {
//     //      console.log('stderr: ' + stderr);            
//     //     }
//     //   if (error !== null) {
//     //     console.log('exec error: ' + error);
//     //   }
//     // });

//     webhook.send('Morgan just fed in this game: info info info json json json', function(err, res) {
//     if (err) {
//         console.log('Error:', err);
//     } else {
//         console.log('Message sent: ', res);
//     }
//     });

// //     web.chat.postMessage('slacktest', 'Morgan just fed in this game: info info info info', function(err, res) {
// //     if (err) {
// //         console.log('Error:', err);
// //     } else {
// //         console.log('Message sent: ', res);
// //     }
// // });

// });
