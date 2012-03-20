/*global module: false*/

var config = {
    secure: true,
    host: 'dfooks-ubuntu64',
    port: 9999,
    webSocketConnectionPrefix: '/echo',
    key: '../certificates/myssl.key',
    cert: '../certificates/myssl.crt',
    ca: '../certificates/myssl.csr'
};

module.exports = config;
