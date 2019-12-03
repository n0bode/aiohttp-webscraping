class Request{
  constructor(message, data){
    this.message = message;
    this.data = data;
  }
}

var connection = null;
async function sendRequest(url, keywords, onrecvdata, finished){
  if (connection != null){
    console.log("Connection is open!");
    return;
  }

  connection = new WebSocket("ws://"+window.location.host+"/ws");
  let req = new Request("request", {"url": url, "keywords":keywords});

	connection.onopen = function(e){
		console.log("Connected to WebSocket Scraping");
    let data = JSON.stringify(req);
    console.log(data);
		connection.send(data);
	};
	
	connection.onmessage = function(msg){
		console.log("Message " + msg.data);
    let data = JSON.parse(msg.data);
    console.log(data);
		if (data["message"] == "response"){
			onrecvdata(data["data"]);
		}
  };
  
  connection.onclose = finished;
	connection.onerror = function(e){
		console.log("Error " + e);
    connection = null;
  };
  
  window.onclose = function(){
    if (connection != null){
      connection.close();
      connection = null;
    }
  }
}
