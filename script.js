const socket = io("http://127.0.0.1:5000");
const canvas = document.getElementById('canvasOutput');
const video = document.querySelector("#videoElement");
const context = canvas.getContext('2d');
const utterance = new SpeechSynthesisUtterance("Warning! Eyes closed for more than 10 seconds");
const FPS = 10;

video.width = 800;
video.height = 600; 

// utility function to throttle the warning message playback 
const throttleFunction=(func, delay)=>{
    // Previously called time of the function
    let prev = 0;
    
    return (...args) => {
        // Current called time of the function
        let now = new Date().getTime();

        // Logging the difference between previously called and current called timings
        console.log(now-prev, delay);
        
        // If difference is greater than delay call the function again.
        if(now - prev > delay){
            prev = now;

            return func(...args); 
        }
    }
}

// throttled callback for when the eyes closed time limit is crossed 
const onLimitReached = throttleFunction(() => { 
    speechSynthesis.speak(utterance);
}, 5000);

// Get the video stream from webcam and playback using the HTML video element 
if (navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function (stream) {
            video.srcObject = stream;
            video.play();
        })
        .catch(function (err) {
            console.log(err)
            console.log("Something went wrong!");
        });
}

// Get the video frame from canvas element and send to server for processing 
setInterval(() => {
    const width = video.width;
    const height = video.height;

    // get new frame from captured and video and draw to canvas 
    context.drawImage(video, 0, 0, width , height );

    // get base64 encoded image 
    const data = canvas.toDataURL('image/jpeg');
    
    // clear canvas from next frame 
    context.clearRect(0, 0, width,height );

    // send image string to server 
    socket.emit('frame', data);
}, 1000/FPS);

// draw processed frames received from the server 
socket.on('response_back', (image) => {
    const image_id = document.getElementById('image');

    image_id.src = image;
});

// when the 10 seconds timi limit is reached 
socket.on('time_limit_reached', (data) => {
    console.log(data);

    const { limit_reached } = JSON.parse(data);

    console.log("time limit crossed: ", limit_reached);

    // if eyes have stayed closed for more than 10 seconds play the warning message
    if(limit_reached === 1){
        onLimitReached();
    }
});