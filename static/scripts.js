let checkSong = () => {
    $.ajax({url: '/song', success: function(song){
        $('#song').val(song.progress / song.duration * 100);
        $('.time').html(Math.floor(song.progress/60000).toLocaleString('en-US', {minimumIntegerDigits: 2, useGrouping:false})
        + ':' + Math.floor((song.progress/1000)%60).toLocaleString('en-US', {minimumIntegerDigits: 2, useGrouping:false})
        + '/' + Math.floor(song.duration/60000).toLocaleString('en-US', {minimumIntegerDigits: 2, useGrouping:false})
        + ':' + Math.floor((song.duration/1000)%60).toLocaleString('en-US', {minimumIntegerDigits: 2, useGrouping:false}));
        if (song.progress < 5000){
            getLyics();
        
        }
        playPause(song.is_playing)
        getSongDetails(song);
        getAlbumCover(song);
        },
        error: function(){
            noAlbumCover();
            noSongDetails();
        }
    });
    setTimeout(checkSong, interval);
}

const getAlbumCover = song => {
    if ($('.album-img img').attr('src') != song.image_link[1].url){
        $('.album-img img').attr('src', song.image_link[1].url)
    }
}

const noAlbumCover = () => {
    if ($('.album-img img').attr('src') != "../static/lost.gif")
    {
        $('.album-img img').attr('src', "../static/lost.gif")
    }
}

const noSongDetails = () => {
    $('label.song-artist').empty();
    $('label.song-name').empty();
    $('.time').html('No song currently playing');
}

let showHideLyrics = button => {
    if ($(".lyrics").css("display") === "none"){
        $(button).html('Hide Lyrics');
        $('.lyrics-link').attr("href", "#show-lyrics");
        $(".lyrics").css("display", "block");
    }
    else {
        $(button).html('Show Lyrics');
        $('.lyrics-link').attr("href", "#top");
        $(".lyrics").css("display", "none");
    }
}

let getSongDetails = (song) => {
    let artists = [];
    song.artists.forEach(artist  => {
        let anchor = document.createElement('a');
        let span = document.createElement('span');
        span.append(anchor);
        anchor.href = artist.link;
        $(anchor).html(artist.name);
        anchor.target = '_blank';
        if (song.artists.length > 0 && song.artists.indexOf(artist) != song.artists.length - 1){
            span.append(' & ');
        }
        artists.push(span);
    });
    if ($('label.song-artist span').length == 0){
        $('label.song-artist').append(artists);
    }else{
        $('label.song-artist span').remove();
        $('label.song-artist').append(artists);
    }
    let a = document.createElement('a');
    a.href = song.link;
    $(a).html(song.name);
    a.target = '_blank';
    if ($('label.song-name a').length == 0){
        $('label.song-name').append(a);
    }else{
        $('label.song-name a').remove();
        $('label.song-name').append(a);
    }
}

let callSongDetails = () => {
    $.ajax({url: '/song', success: function(song){
        getSongDetails(song);
        getAlbumCover(song);
    }});
}

let getLyics = () => {
    $.ajax({url: '/lyrics', success: function(result){
        $('pre').html(result);
    }});
}

let playerOptions = (option) => {
    $.ajax({
        type: "POST",
        url: '/player',
        data: { option: option},
    });
}

let playPause = (songState) => {
    if (songState === true){
        $("#play svg").attr("class", "bi bi-pause-fill");
        $("#play").attr("onclick", "pauseSong()");
        $("#play svg path").attr("d", "M5.5 3.5A1.5 1.5 0 0 1 7 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5zm5 0A1.5 1.5 0 0 1 12 5v6a1.5 1.5 0 0 1-3 0V5a1.5 1.5 0 0 1 1.5-1.5z")
    }
    else {
        $("#play svg").attr("class", "bi bi-play-fill");
        $("#play").attr("onclick", "resumeSong()");
        $("#play svg path").attr("d", "m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z")
    }
}

let pauseSong = () => {
    $.ajax({
        type: "POST",
        url: '/pause',
    });
}

let resumeSong = () => {
    $.ajax({
        type: "POST",
        url: '/play',
    });
}

const light = () => {
    $('#mode svg').html('<path d="M6 .278a.768.768 0 0 1 .08.858 7.208 7.208 0 0 0-.878 3.46c0 4.021 3.278 7.277 7.318 7.277.527 0 1.04-.055 1.533-.16a.787.787 0 0 1 .81.316.733.733 0 0 1-.031.893A8.349 8.349 0 0 1 8.344 16C3.734 16 0 12.286 0 7.71 0 4.266 2.114 1.312 5.124.06A.752.752 0 0 1 6 .278zM4.858 1.311A7.269 7.269 0 0 0 1.025 7.71c0 4.02 3.279 7.276 7.319 7.276a7.316 7.316 0 0 0 5.205-2.162c-.337.042-.68.063-1.029.063-4.61 0-8.343-3.714-8.343-8.29 0-1.167.242-2.278.681-3.286z"/>' +
                        '<path d="M10.794 3.148a.217.217 0 0 1 .412 0l.387 1.162c.173.518.579.924 1.097 1.097l1.162.387a.217.217 0 0 1 0 .412l-1.162.387a1.734 1.734 0 0 0-1.097 1.097l-.387 1.162a.217.217 0 0 1-.412 0l-.387-1.162A1.734 1.734 0 0 0 9.31 6.593l-1.162-.387a.217.217 0 0 1 0-.412l1.162-.387a1.734 1.734 0 0 0 1.097-1.097l.387-1.162zM13.863.099a.145.145 0 0 1 .274 0l.258.774c.115.346.386.617.732.732l.774.258a.145.145 0 0 1 0 .274l-.774.258a1.156 1.156 0 0 0-.732.732l-.258.774a.145.145 0 0 1-.274 0l-.258-.774a1.156 1.156 0 0 0-.732-.732l-.774-.258a.145.145 0 0 1 0-.274l.774-.258c.346-.115.617-.386.732-.732L13.863.1z"/>');
    $('#mode').attr('onclick', 'darkMode()')
}

const dark = () => {
    $('#mode svg').html('<path d="M8 11a3 3 0 1 1 0-6 3 3 0 0 1 0 6zm0 1a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM8 0a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-1 0v-2A.5.5 0 0 1 8 0zm0 13a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-1 0v-2A.5.5 0 0 1 8 13zm8-5a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1 0-1h2a.5.5 0 0 1 .5.5zM3 8a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1 0-1h2A.5.5 0 0 1 3 8zm10.657-5.657a.5.5 0 0 1 0 .707l-1.414 1.415a.5.5 0 1 1-.707-.708l1.414-1.414a.5.5 0 0 1 .707 0zm-9.193 9.193a.5.5 0 0 1 0 .707L3.05 13.657a.5.5 0 0 1-.707-.707l1.414-1.414a.5.5 0 0 1 .707 0zm9.193 2.121a.5.5 0 0 1-.707 0l-1.414-1.414a.5.5 0 0 1 .707-.707l1.414 1.414a.5.5 0 0 1 0 .707zM4.464 4.465a.5.5 0 0 1-.707 0L2.343 3.05a.5.5 0 1 1 .707-.707l1.414 1.414a.5.5 0 0 1 0 .708z"/>');
    $('#mode').attr('onclick', 'ligthMode()')
}

const ligthMode = () => {
    $('link').attr('href', '../static/lightstyles.css');
    light();
    $.ajax({
        type: "POST",
        url: '/mode',
        data: {option: 'light'},
    });
}

const darkMode = () => {
    $('link').attr('href', '../static/darkstyles.css');
    dark();
    $.ajax({
        type: "POST",
        url: '/mode',
        data: {option: 'dark'},
    });
}

let changeMode = (session) => {
    let colorSchemeQueryList = window.matchMedia('(prefers-color-scheme: dark)');

    if (session == 'dark'){
        dark();
    }
    else if(session == 'light'){
        light();
    }
    else{
        const setColorScheme = e => {
            if (e.matches) {
                dark();
            } else {
                light();
            }
        }

        setColorScheme(colorSchemeQueryList);
    }
}

const blurButtons = () => {
    document.addEventListener('click', function(e) { if(document.activeElement.toString() == '[object HTMLButtonElement]'){ document.activeElement.blur(); } });
}
