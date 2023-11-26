const http = require('http');
const { faker } = require('@faker-js/faker');

const host = 'localhost';
const port = 5050;

const requestListener = function (req, res) {
    let fake_value = '';
    const special_separator = '*';  // use this to split query param, eq. q=number*int -> number.int

    let url = req.url;
    url = url.split('=')

    if (url[0] === '/?q') {
        const query = url[1];
        fake_value = eval(`faker.${query.replaceAll(special_separator, '.')}()`)
    }

    res.writeHead(200);
    res.end(fake_value.toString());
};

const server = http.createServer(requestListener);
server.listen(port, host, () => {
    console.log(`Server is running on http://${host}:${port}`);
});
