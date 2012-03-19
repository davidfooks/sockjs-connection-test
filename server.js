/*global require: false */
/*global __dirname: false */
/*global console: false */

var http = require('http');
var sockjs = require('sockjs');
var node_static = require('node-static');

// 1. Echo sockjs server
function do_nothing() {}

var sockjs_opts = {
    sockjs_url: "http://127.0.0.1:9999/sockjs-client.js",
    log: do_nothing
};

var sockjs_echo = sockjs.createServer(sockjs_opts);

var connections = {};
var nextConnectionId = 0;

function publishMessage(message)
{
    var c;
    for (c in connections)
    {
        if (connections.hasOwnProperty(c))
        {
            var connection = connections[c];
            connection.write(message);
        }
    }
}

function sockjs_connection(connection)
{
    var connectionId = nextConnectionId;
    nextConnectionId += 1;

    connections[connectionId] = connection;

    var message = 'Connection from ' + connection.remoteAddress + ':' + connection.remotePort + ' with id ' + connectionId;
    console.log(message);
    publishMessage(message);

    function connection_data(message)
    {
        publishMessage(message);
    }

    function connection_close()
    {
        var message = 'Disconnect from ' + connection.remoteAddress + ':' + connection.remotePort + ' with id? ' + connectionId;
        console.log(message);
        delete connections[connectionId];
        publishMessage(message);
    }

    connection.on('data', connection_data);
    connection.on('close', connection_close);
}

sockjs_echo.on('connection', sockjs_connection);

// 2. Static files server
var static_directory = new node_static.Server(__dirname);

// 3. Usual http stuff
var server = http.createServer();

function static_directory_listener(req, res)
{
    static_directory.serve(req, res);
}

function upgrade_listener(req, res)
{
    res.end();
}

server.addListener('request', static_directory_listener);
server.addListener('upgrade', upgrade_listener);

sockjs_echo.installHandlers(server, {prefix: '/echo'});

console.log(' [*] Listening on 0.0.0.0:9999');
server.listen(9999, '0.0.0.0');
