"""Apply episode-only input corrections after preserving the unmodified narrations."""
from wom15_voice import ROOT,save
EN={'Valentinus':'vælənˈtiːnəs','Filocalus':'fɪˈloʊkələs','kalends':'ˈkælɛndz','Judea':'dʒuːˈdiːə','Aurelian':'ɔːˈɹiːliən','Sol,':'soʊl,','Macrobius':'məˈkɹoʊbiəs','Pliny':'ˈplɪni','Augustine':'ɔːˈɡʌstɪn'}
JA={'最初の行':'最初のぎょう','暦のその行':'暦のそのぎょう','朔日':'ついたち','主は':'しゅは','主が':'しゅが'}
if __name__=='__main__':
 assert (ROOT/'records/first_pass_preserved.json').is_file()
 save(ROOT/'records/approved_reading_corrections.json',{'en':{word:word for word in EN},'ja':JA})
 save(ROOT/'records/english_phoneme_corrections.json',EN)
