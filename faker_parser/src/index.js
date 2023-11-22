const http = require('http');
const { faker } = require('@faker-js/faker');

const host = 'localhost';
const port = 5050;

const requestListener = function (req, res) {
    let url = req.url;
    url = url.split('=')

    if (url[0] === '/q') {
        const query = url[1];
        const fake_value = eval(`faker.${query}()`)
    }


    res.writeHead(200);
    res.end("My first server!");
};

const server = http.createServer(requestListener);
server.listen(port, host, () => {
    console.log(`Server is running on http://${host}:${port}`);
    console.log(faker.number.int())
});
