class Request{
  constructor(message, data){
    this.message = message;
    this.data = data;
  }
}

async function sendRequest(url, keywords, onrecvdata, finished){
  let sock = new WebSocket("ws://"+window.location.host+"/ws");
  let req = new Request("request", {"url": url, "keywords":keywords});

	sock.onopen = function(e){
		console.log("Connected to WebSocket Scraping");
    let data = JSON.stringify(req);
    console.log(data);
		sock.send(data);
	};
	
	sock.onmessage = function(msg){
		console.log("Message " + msg.data);
    let data = JSON.parse(msg.data);
    console.log(data);
		if (data["message"] == "response"){
			onrecvdata(data["data"]);
		}
	};

  sock.onclose = finished;

	sock.onerror = function(e){
		console.log("Error " + e);
		sock = null;
	};
}
