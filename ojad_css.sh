cd ~/.local/share/Anki2/User 1/collection.media

# curl https://www.gavo.t.u-tokyo.ac.jp_ojadbase.css >> _ojadbase.css
# curl https://www.gavo.t.u-tokyo.ac.jp_ojadreset.css >> _ojadreset.css
# curl https://www.gavo.t.u-tokyo.ac.jp_ojadlang_jpn.css >> _ojadlang_jpn.css
# curl https://www.gavo.t.u-tokyo.ac.jp_ojadsans-selif.css >> _ojadsans-selif.css
# curl https://www.gavo.t.u-tokyo.ac.jp_ojadlang_jpn.css >> _ojadlang_jpn.css
# curl https://www.gavo.t.u-tokyo.ac.jp_ojadreset.css >> _ojadreset.css
# curl https://www.gavo.t.u-tokyo.ac.jp_ojadbase.css >> _ojadbase.css
# curl https://www.gavo.t.u-tokyo.ac.jp_ojadsans-selif.css >> _ojadsans-selif.css

curl https://www.gavo.t.u-tokyo.ac.jp/ojad/img/accent.png > _ojad_accent.png

sed -i 's#../img/accent.png#./_ojad_accent.png#g' _ojadmanual_sed.css
