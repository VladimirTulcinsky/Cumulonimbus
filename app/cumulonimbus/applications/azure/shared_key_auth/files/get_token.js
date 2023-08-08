const http = require('http');

module.exports = function (context, req) {
    // If you don't find the solution for this challenge this will help you get a token from the managed identity.



    const { IDENTITY_ENDPOINT, IDENTITY_HEADER } = process.env;
    const url = `${IDENTITY_ENDPOINT}/?resource=https://vault.azure.net&api-version=2019-08-01`;

    const options = {
        headers: {
            'X-IDENTITY-HEADER': IDENTITY_HEADER
        }
    };

    const request = http.get(url, options, (response) => {
        let data = '';

        response.on('data', (chunk) => {
            data += chunk;
        });

        response.on('end', () => {
            context.res = {
                status: 200,
                body: data
            };
            context.done();
        });
    });

    request.on('error', (error) => {
        context.res = {
            status: 500,
            body: `An error occurred: ${error.message}`
        };
        context.done();
    });
};
