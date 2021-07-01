let currentSong = { name: '', artist: '' };
const stylesheet = '#style'

const checkSong = () => {
    $.ajax({
        url: '/api/v0/songs/current', success: function (song, textStatus, xhr) {
            if (xhr.status === 204) {
                noAlbumCover();
                noSongDetails();
                playPause(false);
            }
            else {
                $('#song').val(song.progress / song.duration * 100);
                $('.time').html(Math.floor(song.progress / 60000).toLocaleString('en-US', { minimumIntegerDigits: 2, useGrouping: false })
                    + ':' + Math.floor((song.progress / 1000) % 60).toLocaleString('en-US', { minimumIntegerDigits: 2, useGrouping: false })
                    + '/' + Math.floor(song.duration / 60000).toLocaleString('en-US', { minimumIntegerDigits: 2, useGrouping: false })
                    + ':' + Math.floor((song.duration / 1000) % 60).toLocaleString('en-US', { minimumIntegerDigits: 2, useGrouping: false }));
                if (song.name != currentSong.name || song.artists[0].name != currentSong.artist) {
                    $('#lyrics').html('<div class="loader"></div>')
                    getLyics();
                }
                playPause(song.is_playing)
                $('#song').css("display", "inline-block")
                getSongDetails(song);
                getAlbumCover(song);
                currentSong.name = song.name;
                currentSong.artist = song.artists[0].name;
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
    $('#mode i').attr('class', 'bi bi-moon')
    $('#mode').attr('onclick', 'darkMode()')
}

const dark = () => {
    $('#mode i').attr('class', 'bi bi-triangle')
    $('#mode').attr('onclick', 'pinkMode()')
}

const pink = () => {
    $('#mode i').attr('class', 'bi bi-brightness-high')
    $('#mode').attr('onclick', 'lightMode()')
}

const lightMode = () => {
    $(stylesheet).attr('href', '../static/lightstyles.css');
    light();
    window.localStorage.setItem('mode', 'light');
    $.ajax({
        type: "POST",
        url: '/mode',
        data: { option: 'light' },
    });
}

const darkMode = () => {
    $(stylesheet).attr('href', '../static/darkstyles.css');
    dark();
    window.localStorage.setItem('mode', 'dark');
    $.ajax({
        type: "POST",
        url: '/mode',
        data: { option: 'dark' },
    });
}

const pinkMode = () => {
    $(stylesheet).attr('href', '../static/synthwave.css');
    pink();
    window.localStorage.setItem('mode', 'pink');
    $.ajax({
        type: "POST",
        url: '/mode',
        data: { option: 'pink' },
    });
}


const changeMode = (mode) => {
    let colorSchemeQueryList = window.matchMedia('(prefers-color-scheme: dark)');
    if (mode === 'dark') {
        darkMode();
    }
    else if (mode === 'light') {
        lightMode();
    }
    else if (mode === 'pink') {
        pinkMode();
    }
    else {
        const setColorScheme = e => {
            if (e.matches) {
                dark();
                window.localStorage.setItem('mode', 'dark');
            } else {
                light();
                window.localStorage.setItem('mode', 'light');
            }
        }

        setColorScheme(colorSchemeQueryList);
    }
}

const blurButtons = () => {
    document.addEventListener('click', function (e) { if (document.activeElement.toString() == '[object HTMLButtonElement]') { document.activeElement.blur(); } });
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
        $('i.bi-x').attr('class', 'bi bi-list')
    } else {
        $('i.bi-list').attr('class', 'bi bi-x')
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

const checkIfInstalled = () => {
    if (window.matchMedia('(display-mode: standalone)').matches) {
        $('#installButton').css('display', 'none');
    } else {
        $('#installButton').css('display', 'block');
    }
}
