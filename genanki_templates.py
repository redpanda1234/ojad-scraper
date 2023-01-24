import genanki

automated_ojad_model = genanki.Model(
    4234668442,
    "automated-ojad-card",
    fields=[
        {"name": "textbook_form", "font": "Liberation Sans"},
        {"name": "english", "font": "Liberation Sans"},
        {"name": "example_sentences", "font": "Liberation Sans"},
        {"name": "kanji_meaning", "font": "Liberation Sans"},
        {"name": "part_of_speech", "font": "Liberation Sans"},
        {"name": "pitch_curve_data", "font": "Liberation Sans"},
        {"name": "pitch_curve_reading", "font": "Liberation Sans"},
        {"name": "notes", "font": "Liberation Sans"},
        {"name": "lesson", "font": "Liberation Sans"},
        {"name": "SentenceSound", "font": "Liberation Sans"},
        {"name": "FrontSound", "font": "Liberation Sans"},
    ],
    templates=[
        {
            "name": "Card 1",
            "qfmt": r"""<div class="body-upper" style="border-radius: 5px;">
<div class="lesson">{{lesson}}</div>
<div id="audio" style="display:none">{{FrontSound}}</div>
<div class="soundFront" onclick="playAudio()"></div>
{{textbook_form}}
</div>

<script>
    function playAudio(){
        var audioDiv = document.getElementById('audio');
        var audio = audioDiv.getElementsByTagName("*");
        audio[0].click();
    }
</script>""",
            "afmt": r"""<div class="body-upper" style="border-radius: 5px 5px 0px 0px;">
<div class="lesson">{{lesson}}</div>
<div id="audio" style="display:none">{{FrontSound}}</div>
<div class="soundFront" onclick="playAudio()"></div>
<div>
<link rel="stylesheet" type="text/css" href="_ojadmanual.css?20180709" />
<script type="text/javascript" src="_ojadfunction.js?20180709"></script>
<div class="centered-block">
<div class="phrasing_accent_curve">
<div><canvas id="#phrase_0_0" width="160" height="100"></canvas></div>
</div>

<script type="text/javascript">
$(function () { set_accent_curve_phrase({{text:pitch_curve_data}});});
</script>
<div class="phrasing_text">{{pitch_curve_reading}}</div>
</div>
</div>
{{textbook_form}}
</div>

<div class="body-lower" style="border-radius: 0px 0px 5px 5px;">

<div class="type">{{part_of_speech}}</div><div class="meaning"> {{english}}</div>

<div id="senaudio" style="display:none">{{SentenceSound}}</div>

<div class="sentence">
{{example_sentences}} <i class="fas fa-comment-dots" onclick="playSenAudio()"></i>
</div>


{{#notes}}<div class="notes">
{{notes}}
</div>{{/notes}}

</div>



<script src="https://kit.fontawesome.com/db41768a35.js" crossorigin="anonymous"></script>

<script>
    function playAudio(){
        var audioDiv = document.getElementById('audio');
        var audio = audioDiv.getElementsByTagName("*");
        audio[0].click();
    }
   function playSenAudio(){
        var audioDiv = document.getElementById('senaudio');
        var audio = audioDiv.getElementsByTagName("*");
        audio[0].click();
    }
</script>


""",
        },
    ],
    css=r"""u {
 text-decoration-style: wavy;
text-underline-position: under;
 color: white;
 padding: 1px;
}

.card {
 font-family: UD Digi Kyokasho N-R;
 font-size: 20px;
 text-align: center;
 background-color: #FDF8E9;
 padding: 10px;
}

.body-upper {
 font-family: Noto Sans JP Black;
 font-size: 40px;
 color: #EEE;
 background-color: #555555;
 padding: 40px 10px 10px;
}

.body-lower {
 text-align: left;
 color: #555555;
 background-color: #9FDBDB;
 padding: 20px;
}

.lesson {
 position: absolute;
 background-color: #9FDBDB;
 color: #555555;
 font-size: 20px;
 padding: 5px;
 margin-top: -30px;
}

.meaning {
 width: fit-content;
 font-family: Bree Serif;
 font-size: 15px;
 border: 1px solid #555555;
 padding: 5px;
 margin-bottom: 15px;
 max-width: 100%;
 display: inline-table;
}

.type {
 width: fit-content;
 display: inline-table;
 border: 1px solid #555555;
 background-color: #555555;
 font-family: Bree Serif;
 font-size: 15px;
 color: #9FDBDB;
 padding: 5px;
 padding-left: 7px;
}

.soundFront {
 position: absolute;
 top: 40px;
 right: 40px;
 font-size: 18px;
 content: url("play.png");
 width: 6%;
}

.sentence {
}

.notes {
 font-family: Noto Sans JP Regular;
 font-size: 12px;
 border: 1px dashed #555555;
 padding: 10px;
 margin-top: 20px;
}
.phrasing_accent_curve {
  margin-top: -2em;
  margin-bottom: .25em;
}
.phrasing_text {
  margin-top: -1.25em;
  margin-left: 1em;
  margin-bottom: -3.25em;
  padding-bottom: 3em;
}
""",
)
