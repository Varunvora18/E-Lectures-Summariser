// function displayChapters(){

//     // window.alert("Hi");

trackElement = document.getElementById('indexes');

if ((trackElement) && (textTrack = trackElement.track)){
    if (textTrack.kind === "chapters"){
        window.alert(textTrack.cues.length);
        textTrack.mode = 'hidden';
        for (var i = 0; i < textTrack.cues.length; ++i) {
            cue = textTrack.cues[i],
            chapterName = cue.text,
            start = cue.startTime,
            newLocale = document.createElement("li");
            newLocale.setAttribute('id', start);
            var localeDescription = document.createTextNode(cue.text);
            newLocale.appendChild(localeDescription);
            locationList.insertBefore(newLocale);
            newLocale.addEventListener("click",
            function() {
                video.currentTime = this.id;
            },false);
        }
    textTrack.addEventListener("cuechange",
        function() {
            var currentLocation = this.activeCues[0].startTime;
            if (chapter = document.getElementById(currentLocation)) {
                var locations = [].slice.call(document.querySelectorAll("#chapters li"));
                for (var i = 0; i < locations.length; ++i) { 
                    locations[i].classList.remove("current");
                }
                chapter.classList.add("current");
                locationList.style.top = "-"+chapter.parentNode.offsetTop+"px";
            }
        },false);
    }
}
// }

// // document.getElementById("indexes").addEventListener("onload", function() {
// //     if ((trackElement) && (textTrack = trackElement.track)){
// //         if (textTrack.kind === "chapters"){
// //             textTrack.mode = 'hidden';
// //             for (var i = 0; i < textTrack.cues.length; ++i) {
// //                 cue = textTrack.cues[i],
// //                 chapterName = cue.text,
// //                 start = cue.startTime,
// //                 newLocale = document.createElement("li");
// //                 newLocale.setAttribute('id', start);
// //                 var localeDescription = document.createTextNode(cue.text);
// //                 newLocale.appendChild(localeDescription);
// //                 locationList.insertBefore(newLocale);
// //                 newLocale.addEventListener("click",
// //                 function() {
// //                     video.currentTime = this.id;
// //                 },false);
// //             }
// //         textTrack.addEventListener("cuechange",
// //             function() {
// //                 var currentLocation = this.activeCues[0].startTime;
// //                 if (chapter = document.getElementById(currentLocation)) {
// //                     var locations = [].slice.call(document.querySelectorAll("#chapters li"));
// //                     for (var i = 0; i < locations.length; ++i) { 
// //                         locations[i].classList.remove("current");
// //                     }
// //                     chapter.classList.add("current");
// //                     locationList.style.top = "-"+chapter.parentNode.offsetTop+"px";
// //                 }
// //             },false);
// //         }
// //     }
// // }, false); // here it is

function trial() {
    window.alert('hi');
}

// track.addEventListener('load', displayChapters);