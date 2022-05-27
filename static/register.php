
<!doctype html>
<html>
<head>
 <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Voting System</title>
   
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
   <script src="https://code.jquery.com/jquery-3.6.0.js" integrity="sha256-H+K7U5CnXl1h5ywQfKtSj8PCmoN9aaq30gDh27Xc0jk=" crossorigin="anonymous"></script> 

<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.0/css/all.css" integrity="sha384-lZN37f5QGtY3VHgisS14W3ExzMWZxybE1SJSEsQp9S+oqd12jhcu+A56Ebc1zFSJ" crossorigin="anonymous">
<script>
    if ( window.history.replaceState ) {
        window.history.replaceState( null, null, window.location.href );
    }
</script>
</head>
<body class="bg-light text-dark"> 
   <div class="container shadow-sm p-3 mb-5 bg-white rounded">
  <h3 class="text-center p-3">ELECTRONIC VOTING</h3>
<form id="register-form">
  <div>
    <p class=" bg-warning p-2 text-center">REGISTER</p>
  </div>
  <hr>
  <div class="row">
    <div class="col-lg-12">Server Status: <span id="serverStatus"></span></div>
  </div>
<hr>
  <div class="mb-3 mt-3">
    <label for="name" class="form-label"> Full Name</label>
    <input type="text" class="form-control" id="name" placeholder="Enter Full Name" name="name" req>
  </div>
  <fieldset class="row mb-3">
                  <legend class="col-form-label col-sm-2 pt-0">Gender</legend>
                  <div class="col-sm-10">
                    <div class="form-check">
                      <input class="form-check-input" type="radio" name="gender" id="gridRadios1" value="Male" checked>
                      <label class="form-check-label" for="gridRadios1">
                        Male
                      </label>
                    </div>
                    <div class="form-check">
                      <input class="form-check-input" type="radio" name="gender" id="gridRadios2" value="Female">
                      <label class="form-check-label" for="gridRadios2">
                        Female
                      </label>
                    </div>
                    
                  </div>
                </fieldset>
  <div class="mb-3 mt-3">
    <label for="voteid" class="form-label"> Vote ID</label>
    <input type="text" class="form-control" id="voteId" placeholder="Enter vote ID" name="voteID" req>
  </div>
  <div class="mb-3 mt-3">
    <label for="phone" class="form-label">Phone:</label>
    <input type="phone" class="form-control" id="phone" placeholder="Enter phone" name="phone">
  </div>
 
  <div class="mb-3 mt-3 p-3 bg-primary">
   <label for="fingerId" class="form-label">Fingerprint ID</label>
    <input type="number" class="form-control" placeholder="Enter id (1-127)" name="input_Id" id="input_Id" req>
   <p><button class="btn-danger mt-2" type="button" id="sendId">Send</button></p>
   <div class="row">
     <div class="col-lg-4 p-3  bg-success">
       <p id="finger-print-status">No Finger Detected</p>
     </div>
   
   </div>
  </div>
  <ul class="nav justify-content-end">
    <li class="nav-item m-1">
     <button class="btn btn-primary" id="vote-btn">Register</button>
    </li>
    <li class="nav-item m-1">
      <li class="nav-item">
    <a class="nav-link" href="login.php">Login</a>
  </li>
    </li>
   
  </ul>

</form> 
</div> 
 
 <script>
var socket = new WebSocket('ws:192.168.55.45:8001/ws');
var server_status=document.getElementById('serverStatus');
var  finger_status = document.getElementById('finger-print-status');
var sendId = document.getElementById('sendId');
var finger_Id = document.getElementById('input_Id');
socket.onopen = function () {
console.log('Connected to server');
$('#serverStatus').html('Server Connected');
};
socket.onmessage = function (event) {
var data = JSON.parse(event.data);

if (data.sensor === "finger_print") {
finger_status.innerHTML = data.status;
}
if (data.command === "w") {
var  message = `Wating for a finger`;
finger_status.innerHTML = message;
}
if (data.command === "p") {
var  message = `Processing finger`;
finger_status.innerHTML = message;
}
}

sendId.addEventListener('click', function () {
socket.send(finger_Id.value);
// socket.send(JSON.stringify({
// "sensor": "finger_print",
// "status": "voted"
// }));
});
 var name = $("#uname").val();
 var gender = $("gender").val();
 var phone = $("#phone").val();
 var voteId = $("#voteId").val();
 var fingerId = finger_Id.val();

$("#vote-btn").click(function() {
  alert(gender);
    $.ajax({
          type: "POST",
          url: "actionpages/registration.php",
          data: {
            name: name,
            email: email,
            phone: phone,
            pass: pass
                },
          cache: false,
          success: function(data) {
            alert(data);
            if(data=="success"){
            $("#success").show();
                $('#success').html('Registerd Succesful');
                $('#register-form').trigger("reset");                        
            }else {
                $("#error").show();
                 $('#error').html('Error Occured');
            }
},
                    error: function(xhr, status, error) {
                       // alert(error);
                    }
                });
 });

socket.onclose = function () {
console.log('Network Disconneted');
};

</script>
</body>
</html>