import PubSub from 'pubsub-js'

var socket = new WebSocket("wss://" + window.location.host + "/");

socket.onmessage = function(e) {
    console.log(e.data)
    const message = JSON.parse(e.data)
    if (message.event) {
        PubSub.publish(message.event, message.data);
        // $(document).trigger(message.event, message.data);
    }
}

socket.onopen = function(e) {
    console.log('websocket connected')
}

socket.trigger = function(event, data) {
    const message = {task: event, data: data}    
    socket.send(JSON.stringify(message))
}

export default socket
