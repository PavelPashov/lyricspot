let currentSong;
const checkSong = () => {
    $.ajax({
        url: '/api/v0/songs/current', success: function (song, textStatus, xhr) {
            if (xhr.status === 204) {
                noAlbumCover();
                noSongDetails();
                playPause(false)
            }
            else {
                $('#song').val(song.progress / song.duration * 100);
                $('.time').html(Math.floor(song.progress / 60000).toLocaleString('en-US', { minimumIntegerDigits: 2, useGrouping: false })
                    + ':' + Math.floor((song.progress / 1000) % 60).toLocaleString('en-US', { minimumIntegerDigits: 2, useGrouping: false })
                    + '/' + Math.floor(song.duration / 60000).toLocaleString('en-US', { minimumIntegerDigits: 2, useGrouping: false })
                    + ':' + Math.floor((song.duration / 1000) % 60).toLocaleString('en-US', { minimumIntegerDigits: 2, useGrouping: false }));
                if (song.progress < 5000 && currentSong != song.name) {
                    $('#lyrics').html('<div class="loader"></div>')
                    getLyics();
                }
                playPause(song.is_playing)
                $('#song').css("display", "inline-block")
                getSongDetails(song);
                getAlbumCover(song);
                currentSong = song.name;
            }
        },
        error: function () {
            noAlbumCover();
            noSongDetails();
        }
    });
    setTimeout(checkSong, interval);
}

const getAlbumCover = song => {
    if ($('.album-img').attr('src') != song.image_link[1].url) {
        $('.album-img img').attr('src', song.image_link[1].url)
        $('.album-img').css('display', "block")
        $('.album-loader-wrap').css('display', 'none')
    }
}

const noAlbumCover = () => {
    if ($('.album-loader-wrap').css('display') == "none") {
        $('.album-loader-wrap').css('display', "block")
        $('.album-img').css('display', 'none')
    }
}

const noSongDetails = () => {
    $('label.song-artist').empty();
    $('label.song-name').empty();
    $('#song').css("display", "none")
    $('.time').html('Nothing is playing <br/> <br/>Play a song from your Spotify account!');
}

const showHideLyrics = button => {
    if ($(".lyrics").css("display") === "none") {
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

const getSongDetails = (song) => {
    let artists = [];
    song.artists.forEach(artist => {
        let anchor = document.createElement('a');
        let span = document.createElement('span');
        span.append(anchor);
        anchor.href = artist.link;
        $(anchor).html(artist.name);
        anchor.target = '_blank';
        if (song.artists.length > 0 && song.artists.indexOf(artist) != song.artists.length - 1) {
            span.append(' & ');
        }
        artists.push(span);
    });
    if ($('label.song-artist span').length == 0) {
        $('label.song-artist').append(artists);
    } else {
        $('label.song-artist span').remove();
        $('label.song-artist').append(artists);
    }
    let a = document.createElement('a');
    a.href = song.link;
    $(a).html(song.name);
    a.target = '_blank';
    if ($('label.song-name a').length == 0) {
        $('label.song-name').append(a);
    } else {
        $('label.song-name a').remove();
        $('label.song-name').append(a);
    }
}

const callSongDetails = () => {
    $.ajax({
        url: '/api/v0/songs/current', success: function (song) {
            getSongDetails(song);
            getAlbumCover(song);
        }
    });
}

const getLyics = () => {
    $.ajax({
        url: '/api/v0/songs/lyrics', success: function (result) {
            $('pre').html(result);
        }
    });
}

const playerOptions = (option) => {
    $.ajax({
        type: "POST",
        url: '/player',
        data: { option: option },
    });
}

const playPause = (songState) => {
    if (songState === true) {
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

const pauseSong = () => {
    $.ajax({
        type: "POST",
        url: '/pause',
    });
}

const resumeSong = () => {
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
        data: { option: 'light' },
    });
}

const darkMode = () => {
    $('link').attr('href', '../static/darkstyles.css');
    dark();
    $.ajax({
        type: "POST",
        url: '/mode',
        data: { option: 'dark' },
    });
}

const changeMode = (session) => {
    let colorSchemeQueryList = window.matchMedia('(prefers-color-scheme: dark)');

    if (session == 'dark') {
        dark();
    }
    else if (session == 'light') {
        light();
    }
    else {
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
    document.addEventListener('click', function (e) { if (document.activeElement.toString() == '[object HTMLButtonElement]') { document.activeElement.blur(); } });
}

const mariya = () => {
    let param = window.location.search.substring(1);
    if (param === 'mariya') {
        $('link').attr('href', '../static/mariya.css');
    }
}

const hideButton = (element) => {
    $(element).css("display", "none");
    $('.loader-wrap').css("display", "block");
}


const checkProgress = (project = null) => {
    $.ajax({
        type: "POST",
        url: '/check',
        data: { project: project },
        success: function (collProgress) {
            $('#collection_progress').val(parseInt(collProgress));
            $('#collection_progress ~ p').html(`${collProgress}%`)
        }
    });
}

const updateCollProgress = () => {
    checkProgress();
    if ($('#collection_progress').val() != '100') {
        setTimeout(updateCollProgress, interval);
    }
    else {
        $('h3').html('All done!')
        $('.collection-link p').css("display", "none");
        $('.collection-link a').css("display", "block");
    }
}

const showHideMenu = () => {
    const menu = $('#mobileLinks')
    if (menu.css('display') === 'flex') {
        menu.css('display', 'none');
    } else {
        menu.css('display', 'flex');
    }
}


const getTopSogns = (element) => {
    term = $(element).attr('data-term')
    $.ajax({
        url: `/api/v0/songs/top/term/${term}_term`, success: function (data) {
            $('.card').each(function (i, card) {
                $(card).find('.card-img img').attr('src', data.songs[i].image_link)
                $(card).find('.card-name a').attr('href', data.songs[i].link)
                $(card).find('.card-name a').html(data.songs[i].name)
                $(card).find('.card-artist a').attr('href', data.songs[i].artists[0].link)
                $(card).find('.card-artist a').html(data.songs[i].artists[0].name)
            })
            $('.active').attr('class', 'not-active')
            $(element).attr('class', 'active')
        }
    });
}
