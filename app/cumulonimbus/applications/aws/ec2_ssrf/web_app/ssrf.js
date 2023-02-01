var express = require('express');
var axios = require('axios');
var app = express();

app.get('/', function (req, res) {
  var url = 'https://vintagekitchennotes.com/homemade-frangipane-almond-cream/';
  res.send(`<html>
        <head>
          <title>SSRF</title>
        </head>
        <body>
          <h1>Welcome Bakers</h1>
          <div>You probably wanted to check our amazing Super Secret Recipe for Frangipane (SSRF) here?: <a href='/recipe?url=${url}'>/recipe?url=${url}</a></div>
        </body>
      </html>`);
});

app.get('/recipe', function (req, res) {
  var target = req.query.url || 'https://vintagekitchennotes.com/homemade-frangipane-almond-cream/';
  axios.get(target)
    .then(function (response) {
      if (response.headers['Content-Type'] !== 'text/html') {
        res.send(JSON.stringify(response.data));
      } else {
        res.send(`
          <html>
            <head>
              <title>SSRF</title>
            </head>
            <body>
              <h1>SSRF</h1>
              <div>${response.data}</div>
            </body>
          </html>`);
      }
    })
    .catch(function (error) {
      res.status(500).send(error.message);
    });
});


app.get('*', function (req, res) {
  var url = 'https://vintagekitchennotes.com/homemade-frangipane-almond-cream/';
  res.send(`<html>
        <head>
          <title>404</title>
        </head>
        <body>
          <h1>Nothing here</h1>
          <div>You probably wanted to check our amazing recipe here?: <a href='/recipe?url=${url}'>/recipe?url=${url}</a></div>
        </body>
      </html>`);
});


app.listen(80, function () {
  console.log('Example app listening on port 80!');
});
