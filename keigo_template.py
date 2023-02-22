import genanki

keigo_card = genanki.Model(
    4234668443,
    "keigo-card",
    fields=[
        {"name": "plain", "font": "Liberation Sans"},
        {"name": "sonkeigo", "font": "Liberation Sans"},
        {"name": "sonkeigo-masu", "font": "Liberation Sans"},
        {"name": "sonkeigo-example", "font": "Liberation Sans"},
        {"name": "sonkeigo-alt", "font": "Liberation Sans"},
        {"name": "sonkeigo-alt-masu", "font": "Liberation Sans"},
        {"name": "sonkeigo-alt-example", "font": "Liberation Sans"},
        {"name": "kenjougo-1", "font": "Liberation Sans"},
        {"name": "kenjougo-1-masu", "font": "Liberation Sans"},
        {"name": "kenjougo-1-example", "font": "Liberation Sans"},
        {"name": "kenjougo-1-alt", "font": "Liberation Sans"},
        {"name": "kenjougo-1-alt-masu", "font": "Liberation Sans"},
        {"name": "kenjougo-2", "font": "Liberation Sans"},
        {"name": "kenjougo-2-masu", "font": "Liberation Sans"},
        {"name": "teineigo", "font": "Liberation Sans"},
    ],
    templates=[
        {
            "name": "Card 1",
            "qfmt": r"""<div class="body-upper" style="border-radius: 5px;">
<div class="lesson">L.6-keigo</div>
尊敬語 for {{plain}}
</div>
""",
            "afmt": r"""<div class="body-upper" style="border-radius: 5px 5px 0px 0px;">
<div class="lesson">L.6-keigo</div>
<div>
<link rel="stylesheet" type="text/css" href="_ojadmanual.css?20180709" />
<script type="text/javascript" src="_ojadfunction.js?20180709"></script>
<div class="centered-block">
<div class="phrasing_accent_curve">
<div><canvas id="#phrase_0_0" width="160" height="100"></canvas></div>
</div>

<script type="text/javascript">
$(function () { set_accent_curve_phrase();});
</script>
<div class="phrasing_text"></div>
</div>
</div>
{{plain}}
</div>

<div class="body-lower" style="border-radius: 0px 0px 5px 5px;">

<div class="type">尊敬語</div><div class="meaning"> for {{plain}}</div>

<div class="sentence">
<ul>
<li>{{sonkeigo}}<br>{{sonkeigo-masu}}
{{#sonkeigo-example}}
<li> Example: {{sonkeigo-example}}
{{/sonkeigo-example}}
</ul>
</div>
{{#sonkeigo-alt}}
</ul>
Alt:
<ul>
<li> {{sonkeigo-alt}} <br> {{sonkeigo-alt-masu}}
{{#sonkeigo-alt-example}}
<li> Example: {{sonkeigo-alt-example}}
{{/sonkeigo-alt-example}}
</ul>
{{/sonkeigo-alt}}
</div>
""",
        },
        {
            "name": "Card 2",
            "qfmt": r"""{{#kenjougo-1}}
<div class="body-upper" style="border-radius: 5px;">
<div class="lesson">L.6-keigo</div>
Class I 謙譲語 for {{plain}}
</div>
{{/kenjougo-1}}
""",
            "afmt": r"""<div class="body-upper" style="border-radius: 5px 5px 0px 0px;">
<div class="lesson">L.6-keigo</div>
<div>
<link rel="stylesheet" type="text/css" href="_ojadmanual.css?20180709" />
<script type="text/javascript" src="_ojadfunction.js?20180709"></script>
<div class="centered-block">
<div class="phrasing_accent_curve">
<div><canvas id="#phrase_0_0" width="160" height="100"></canvas></div>
</div>

<script type="text/javascript">
$(function () { set_accent_curve_phrase();});
</script>
<div class="phrasing_text"></div>
</div>
</div>
{{plain}}
</div>

<div class="body-lower" style="border-radius: 0px 0px 5px 5px;">

<div class="type">謙譲語-I</div><div class="meaning"> for {{plain}}</div>

<div class="sentence">
<ul>
<li>{{kenjougo-1}}<br>{{kenjougo-1-masu}}
{{#kenjougo-1-example}}
<li> Example: {{kenjougo-1-example}}
{{/kenjougo-1-example}}
</ul>
</div>
{{#kenjougo-1-alt}}
</ul>
Alt:
<ul>
<li> {{kenjougo-1-alt}} <br> {{kenjougo-1-alt-masu}}
</ul>
{{/kenjougo-1-alt}}
</div>
""",
        },
        {
            "name": "Card 3",
            "qfmt": r"""{{#kenjougo-2}}
<div class="body-upper" style="border-radius: 5px;">
<div class="lesson">L.6-keigo</div>
Class II 謙譲語 for {{plain}}
</div>
{{/kenjougo-2}}
""",
            "afmt": r"""<div class="body-upper" style="border-radius: 5px 5px 0px 0px;">
<div class="lesson">L.6-keigo</div>
<div>
<link rel="stylesheet" type="text/css" href="_ojadmanual.css?20180709" />
<script type="text/javascript" src="_ojadfunction.js?20180709"></script>
<div class="centered-block">
<div class="phrasing_accent_curve">
<div><canvas id="#phrase_0_0" width="160" height="100"></canvas></div>
</div>

<script type="text/javascript">
$(function () { set_accent_curve_phrase();});
</script>
<div class="phrasing_text"></div>
</div>
</div>
{{plain}}
</div>

<div class="body-lower" style="border-radius: 0px 0px 5px 5px;">

<div class="type">謙譲語-II</div><div class="meaning"> for {{plain}}</div>

<div class="sentence">
<ul>
<li>{{kenjougo-2}}<br>{{kenjougo-2-masu}}
</ul>
</div>
{{#kenjougo-2-alt}}
</ul>
</div>
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
  margin-left: .375em;
  margin-bottom: -3.25em;
  padding-bottom: 3em;
}
""",
)
