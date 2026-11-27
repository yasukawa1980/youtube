"""Input-only corrections based on first-pass phonemes and VOICEVOX queries."""
from wom16_voice import ROOT,save
EN={'sirène':'see-REN','sirena':'see-RAY-nah','Boeotia':'bee-OH-shuh','Euripides':'yoo-RIP-ih-deez','Ovid':'OV-id','Isidore':'IZ-ih-dor'}
PH={'see-REN':'siːɹˈɛn','see-RAY-nah':'siːɹˈeɪnə','bee-OH-shuh':'biːˈoʊʃə','yoo-RIP-ih-deez':'jʊɹˈɪpɪdiːz','OV-id':'ˈɑːvɪd','IZ-ih-dor':'ˈɪzɪdɔːɹ'}
JA={'臍':'へそ','ヘレネ':'へれね'}
if __name__=='__main__':
    assert (ROOT/'records/first_pass_preserved.json').exists()
    save(ROOT/'records/approved_reading_corrections.json',{'en':EN,'ja':JA})
    save(ROOT/'records/english_phoneme_corrections.json',PH)
