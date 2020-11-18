msgchi
------
Creating a translation catalog for chinese locales.

Description
-----------
The input file is a template POT file, or a translated PO file for another chinese language.

Dictionaries are UTF-8 coded text files with the format in each line:
Source Words|Translated Words
(Source Words are lower case; Source Words with pre/surfix [-] or ["] for internal use.)
(Excluded single word: be, being, been, am, are, is, was, were; have, having, has, had)

Install
-----------
	make
	make install

License
-----------
* The script files are released under GPL.
* The dictionary files are released under Public Domain.

Program Reference
-----------------
* stcc by Ling Li, Yuan-Chen Cheng
* webpot by Ping Yeh
* msghack by Trond Eivind Glomsrød
* tw2hk.pl by Abel Cheung
* opencc by Carbo Kuo

Dictionary Reference
--------------------
* eng2cmn
	* CPATCH <http://glossary.pank.org/>
	* CMEX 「兩岸資訊及通信術語對照表」
	* 英中繁簡編程術語對照 <http://jjhou.boolan.com/terms.htm>
	* Translation Project <http://translationproject.org/>
* cmn2yue
	* 曾焯文《粵辭正典─健康篇》
	* 邵慧君、甘于恩《粵語詞彙講義》
	* 陳雄根、張錦少《粵語詞匯溯源》
	* 現代標準漢語與粵語對照資料庫 <https://apps.itsc.cuhk.edu.hk/hanyu/>
* cmn2nan
	* 教育部臺灣閩南語常用詞辭典 <https://twblg.dict.edu.tw/holodict_new/>
	* 潘科元台語文理想國 <https://blog.xuite.net/khoguan/blog>
	* 愛台語 <https://itaigi.tw/>
	* 陳世明、陳文彥《臺語漢字學》
* cmn2hak
	* 客家委員會客語辭彙 <https://cloud.hakka.gov.tw/details?p=126632>

Author
------
趙惟倫(Wei-Lun Chao) <bluebat@member.fsf.org>
