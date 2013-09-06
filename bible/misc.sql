-- Misc SQL for the database

--  RegExp that matches References (short book names)
 select * from verse where ref !~* '^[A-Za-z0-9]{3} [0-9]{0,3}((:[0-9]{0,3})|()|(:Title))$';

-- RegExp that finds any reference that do NOT match a valid reference
 select * from import_hymn_verse where ref !~*
  '^((1 Chron)|(1 Cor)|(1 John)|(1 Kings)|(1 Pet)|(1 Sam)|(1 Thes)|(1 Tim)|(2 Chron)|(2 Cor)|(2 John)|(2 Kings)|(2 Pet)|(2 Sam)|(2 Thes)|(2 Tim)|(3 John)|(Acts)|(Amos)|(Col)|(Dan)|(Deut)|(Eccl)|(Eph)|(Esth)|(Exo)|(Ezek)|(Ezra)|(Gal)|(Gen)|(Hab)|(Hag)|(Heb)|(Hosea)|(Isa)|(James)|(Jer)|(Job)|(Joel)|(John)|(Jonah)|(Josh)|(Jude)|(Judg)|(Lam)|(Lev)|(Luke)|(Mal)|(Mark)|(Matt)|(Micah)|(Nahum)|(Neh)|(Num)|(Obad)|(Phil)|(Philem)|(Prov)|(Psa)|(Rev)|(Rom)|(Ruth)|(SS)|(Titus)|(Zech)|(Zeph)) [0-9]{0,3}[:]{0,1}(([0-9]{0,3})|()|(Title))(( *- *[0-9]{0,3}[:]{0,1}[0-9]{1,3})|())$';


-- RegExp that matches a reference to a range of verses
 select * from import_hymn_verse where ref ~* 
  '^((1 Chron)|(1 Cor)|(1 John)|(1 Kings)|(1 Pet)|(1 Sam)|(1 Thes)|(1 Tim)|(2 Chron)|(2 Cor)|(2 John)|(2 Kings)|(2 Pet)|(2 Sam)|(2 Thes)|(2 Tim)|(3 John)|(Acts)|(Amos)|(Col)|(Dan)|(Deut)|(Eccl)|(Eph)|(Esth)|(Exo)|(Ezek)|(Ezra)|(Gal)|(Gen)|(Hab)|(Hag)|(Heb)|(Hosea)|(Isa)|(James)|(Jer)|(Job)|(Joel)|(John)|(Jonah)|(Josh)|(Jude)|(Judg)|(Lam)|(Lev)|(Luke)|(Mal)|(Mark)|(Matt)|(Micah)|(Nahum)|(Neh)|(Num)|(Obad)|(Phil)|(Philem)|(Prov)|(Psa)|(Rev)|(Rom)|(Ruth)|(SS)|(Titus)|(Zech)|(Zeph)) [0-9]{0,3}[:]{0,1}(([0-9]{0,3})|()|) *- *[0-9]{0,3}[:]{0,1}[0-9]{1,3}$';

-- Official Abbreviations
 Gen Exo Lev Num Deut Josh Judg Ruth 1 Sam 2 Sam 1 Kings 2 Kings 1 Chron 
 2 Chron Ezra Neh Esth Job Psa Prov Eccl SS Isa Jer Lam Ezek Dan Hosea Joel
 Amos Obad Jonah Micah Nahum Hab Zeph Hag Zech Mal 
 Matt Mark Luke John Acts Rom 1 Cor 2 Cor Gal Eph Phil Col 1 Thes 2 Thes 1 Tim 
 2 Tim Titus Philem Heb James 1 Pet 2 Pet 1 John 2 John 3 John Jude Rev

Calgary Songbook hymns
 16, 28, 39, 41, 65, 66, 70, 82, 116, 124, 152, 156, 162, 166, 172, 204, 205, 206,208,250,
 251,255,264,267, 268, 294, 298, 299, 301, 306, 308, 309, 310, 313, 317, 322, 323, 325, 348, 
 350, 371, 373, 378, 383, 389, 394, 395, 396, 403, 426, 431, 432, 433, 434, 435, 437, 438, 441, 
 445, 456, 471, 473, 481, 493, 497, 498, 499, 501, 505, 507, 509, 512, 513, 514, 521, 523, 539, 
 542, 544, 545, 546, 548, 554, 559, 564, 569, 575, 578, 579, 582, 599, 600, 602, 639, 642, 643, 
 645, 669, 711, 713, 717, 720, 723, 770, 775, 784, 789, 811, 812, 824, 841, 846, 852, 871, 880, 
 881,885,886,887,889,890,893,894,904,921,938,948,960,971,993,1006,1007,1008,1009,1010,1017,1023,
 1024,1025,1043,1048,1050,1051,1057,1066,1068,1070,1079,1080,1083,1084,1085,1086,1096,1103,1113,1117,
 1119,1123,1127,1129,1131,1141,1142,1143,1145,1148,1149,1150,1151,1152,1153,1154,1158,1159,1162,1170,
 1178,1179,1191,1193,1196,1197,1198,1199,1205,1206,1208,1216,1221,1222,1226,1232,1233,1234,1237,
 1238,1248,1251,1252,1255,1256,1260,1266,1273,1278,1282,1283,1287,1293,1294,1297,1299,1304,1307,
 1308,1315,1325,1326,1327,1328,1331,1333,1334,1335,1336,1337,1338,1339,1340,1341,1343,1345,1346,1347



-- Hymns with multiple/different choruses (fixed)
-- last chorus different--
13,275, 283,447,1060,1080,1110,1160,1219,1257,1259,1286

all choruses different 
273,276,386,770,989,1017,1081,1116,1135,1144,1145,1146,1156,1157,1165,1173,1175,1176,1177,1178,1180,1190,1200
1214,1224,1226,1233,1242,1247,1252,1261,1270,1271,1307,1308,1328,1351


-- Determine if any repeated choruses have non-continguous id numbers (a sign that we might be removing something incorrectly)
select hnum, diff, line_count from 
  (select hnum, (max(id)-min(id)) as diff, max(line) as line_count, max(id) as max_id, min(id) as min_id from hymn_line where id in
    (select id
     from (select max(id) as id, count(*) as count, hnum, stanza, line, data from hymn_line group by hnum, stanza, line, data) a
     where count > 1)
  group by hnum) d
where (d.line_count::int - d.diff) != 1
order by hnum
;


-- Find hymns with multiple choruses (that are the same)
select * from hymn_line where id in 
  (select id 
   from (select max(id) as id, count(*) as count, hnum, stanza, line, data 
         from hymn_line 
         where hnum != 460 -- Special handling (multiple versions)
           and stanza = 'c'
           and type='data'
           and hnum < 1500
         group by hnum, stanza, line, data 
        ) a 
   where count > 1) 
order by hnum, lineorder;


delete from hymn_line where id in 
(select id
   from (select max(id) as id, count(*) as count, hnum, stanza, line, data
         from hymn_line
         where hnum != 460 -- Special handling (multiple versions)
           and stanza = 'c'
           and type='data'
           and hnum < 1500
         group by hnum, stanza, line, data
        ) a
   where count > 1)




