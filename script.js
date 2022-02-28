const socket = io("http://127.0.0.1:5000");
const canvas = document.getElementById('canvasOutput');
const video = document.querySelector("#videoElement");
const context = canvas.getContext('2d');
const utterance = new SpeechSynthesisUtterance("Warning! Eyes closed for more than 10 seconds");
const FPS = 10;

let time_limit_reached = false;
let startTime, endTime;

video.width = 800;
video.height = 600; 

function start() {
    startTime = performance.now();
};
  
function end() {
    endTime = performance.now();
    var timeDiff = endTime - startTime; //in ms 
    // strip the ms 
    timeDiff /= 1000; 

    // get seconds 
    var seconds = Math.round(timeDiff);
    
    console.log(seconds + " seconds");

    return seconds;
}

function debounce(func, timeout = 500) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => { func.apply(this, args); }, timeout);
    };
}

const throttleFunction=(func, delay)=>{
    // Previously called time of the function
    let prev = 0;
    
    return (...args) => {
        // Current called time of the function
        let now = new Date().getTime();

        // Logging the difference between previously
        // called and current called timings
        console.log(now-prev, delay);
        
        // If difference is greater than delay call
        // the function again.
        if(now - prev> delay){
            prev = now;

            // "..." is the spread operator here
            // returning the function with the
            // array of arguments
            return func(...args); 
        }
    }
}

const onLimitReached = throttleFunction(() => { 
    speechSynthesis.speak(utterance);
}, 5000);

if (navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function (stream) {
            video.srcObject = stream;
            video.play();
        })
        .catch(function (err0r) {
            console.log(err0r)
            console.log("Something went wrong!");
        });
}

setInterval(() => {
    const width = video.width;
    const height = video.height;

    context.drawImage(video, 0, 0, width , height );

    const data = canvas.toDataURL('image/jpeg');
    
    context.clearRect(0, 0, width,height );

    socket.emit('frame', data);
}, 1000/FPS);

socket.on('response_back', (image) => {
    const image_id = document.getElementById('image');
    image_id.src = image;
});

socket.on('time_limit_reached', (data) => {
    console.log(data);

    const { limit_reached } = JSON.parse(data);

    console.log("time limit crossed: ", limit_reached);

    if(limit_reached === 1){
        onLimitReached();
    }
});