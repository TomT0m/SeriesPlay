#!/usr/bin/python
#encoding:utf-8
""" Unittest for TPB magnet search module"""

from twisted.trial import unittest
from datasource.play_tpb_search import TPBMagnetFinder, ConnectionException #*

__sample_html__ = """
<!DOCTYPE html PUBLIC "-W3CDTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" >
<head>
	<title>The Pirate Bay - The galaxy's most resilient bittorrent site</title>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
	<link rel="search" type="application/opensearchdescription+xml" href="//static.thepiratebay.se/opensearch.xml" title="Search The Pirate Bay" />
	<link rel="stylesheet" type="text/css" href="//static.thepiratebay.se/css/pirate6.css"/>
	<style type="text/css">
		.searchBox{
			margin: 6px;
			width: 300px;
			vertical-align: middle;
			padding: 2px;
		        background-image:url('//static.thepiratebay.se/img/icon-https.gif');
        		background-repeat:no-repeat;
		        background-position: right;
		}

		.detLink {
			font-size: 1.2em;
			font-weight: 400;
		}
		.detDesc {
			color: #4e5456;
		}
		.detDesc a:hover {
			color: #000099;
			text-decoration: underline;
		}
		.sortby {
			text-align: left;
			float: left;
		}
		.detName {
			padding-top: 3px;
			padding-bottom: 2px;
		}
		.viewswitch {
			font-style: normal;
			float: right;
			text-align: right;
			font-weight: normal;
		}
	</style>
	<script src="//static.thepiratebay.se/js/tpb.js" type="text/javascript"></script>

        <style type="text/css">
		table#sponsoredLinks a { border: 0; }
		table#sponsoredLinks a:hover { text-decoration: underline; }
                table#sponsoredLinks td.downbut a {border: none;}
                table#sponsoredLinks {min-width: 400px; text-align: left; width: 100%; margin: 0 0 10px 0; border-left: solid 1px #ffffff;}
                table#sponsoredLinks th {padding: 7px; background-color: #D2B9A6;}
		table#sponsoredLinks td {padding: 2px 4px; background-color: #F6F1EE; font-weight: bold; font-style: italic; text-align: right; white-space: nowrap;}
                table#sponsoredLinks td img {border: 0;}
                table#sponsoredLinks td.first {font-style: normal; text-align: left;}
                table#sponsoredLinks td.first img {margin: 0 5px 0 0; vertical-align: -7px;}
                table#sponsoredLinks tr:hover td {background-color: #FFFFFF;}
                table#sponsoredLinks td.downbut {width: 170px;}
        </style>

	<script language="javascript" type="text/javascript">if (top.location != self.location) {top.location.replace(self.location);}</script>
</head>

<body>
	<div id="header">

		<!-- top468 -->
		<div class="ad">

<script type="text/javascript">
pb_cid='BAYBANNER468X60_1';
pb_type='banner_468x60';
</script>
<script src="http://clkads.com/banners/script/include_img_banner.js" type="text/javascript"></script>
		</div>
		<form method="get" id="q" action="/s/">
			<a href="/" class="img"><img src="//static.thepiratebay.se/img/tpblogo_sm_ny.gif" id="TPBlogo" alt="The Pirate Bay" /></a>
			<b><a href="/" title="Search Torrents">Search Torrents</a></b>&nbsp;&nbsp;|&nbsp;
			<a href="/browse" title="Browse Torrents">Browse Torrents</a>&nbsp;&nbsp;|&nbsp;

			<a href="/recent" title="Recent Torrent">Recent Torrents</a>&nbsp;&nbsp;|&nbsp;
			<a href="/tv" title="TV shows">TV shows</a>&nbsp;&nbsp;|&nbsp;
			<a href="/music" title="Music">Music</a>&nbsp;&nbsp;|&nbsp;
			<a href="/top" title="Top 100">Top 100</a>
			<br /><input type="search" class="inputbox" title="Pirate Search" name="q" placeholder="Search here..." value="house s02e07" /><input value="Pirate Search" type="submit" class="submitbutton" /><br />			<label for="audio" title="Audio"><input id="audio" name="audio" onclick="javascript:rmAll();" type="checkbox"/>Audio</label>

			<label for="video" title="Video"><input id="video" name="video" onclick="javascript:rmAll();" type="checkbox"/>Video</label>
			<label for="apps" title="Applications"><input id="apps" name="apps" onclick="javascript:rmAll();" type="checkbox"/>Applications</label>
			<label for="games" title="Games"><input id="games" name="games" onclick="javascript:rmAll();" type="checkbox"/>Games</label>
			<label for="porn" title="Porn"><input id="porn" name="porn" onclick="javascript:rmAll();" type="checkbox"/>Porn</label>
			<label for="other" title="Other"><input id="other" name="other" onclick="javascript:rmAll();" type="checkbox"/>Other</label>

			<select id="category" name="category" onchange="javascript:setAll();">

        	        	<option value="0">All</option>
				<optgroup label="Audio">
					<option value="101">Music</option>
					<option value="102">Audio books</option>
					<option value="103">Sound clips</option>
					<option value="104">FLAC</option>

					<option value="199">Other</option>
				</optgroup>
				<optgroup label="Video">
					<option value="201">Movies</option>
					<option value="202">Movies DVDR</option>
					<option value="203">Music videos</option>
					<option value="204">Movie clips</option>

					<option value="205">TV shows</option>
					<option value="206">Handheld</option>
					<option value="207">Highres - Movies</option>
					<option value="208">Highres - TV shows</option>
					<option value="209">3D</option>
					<option value="299">Other</option>

				</optgroup>
				<optgroup label="Applications">
					<option value="301">Windows</option>
					<option value="302">Mac</option>
					<option value="303">UNIX</option>
					<option value="304">Handheld</option>
					<option value="305">IOS (iPad/iPhone)</option>

					<option value="306">Android</option>
					<option value="399">Other OS</option>
				</optgroup>
				<optgroup label="Games">
					<option value="401">PC</option>
					<option value="402">Mac</option>
					<option value="403">PSx</option>

					<option value="404">XBOX360</option>
					<option value="405">Wii</option>
					<option value="406">Handheld</option>
					<option value="407">IOS (iPad/iPhone)</option>
					<option value="408">Android</option>
					<option value="499">Other</option>

				</optgroup>
				<optgroup label="Porn">
					<option value="501">Movies</option>
					<option value="502">Movies DVDR</option>
					<option value="503">Pictures</option>
					<option value="504">Games</option>
					<option value="505">HighRes - Movies</option>

					<option value="506">Movie clips</option>
					<option value="599">Other</option>
				</optgroup>
				<optgroup label="Other">
					<option value="601">E-books</option>
					<option value="602">Comics</option>
					<option value="603">Pictures</option>

					<option value="604">Covers</option>
					<option value="605">Physibles</option>
					<option value="699">Other</option>
				</optgroup>
			</select>

			<input type="hidden" name="page" value="0" />
			<input type="hidden" name="orderby" value="99" />

		</form>
	</div><!-- // div:header -->

	<h2><span>Search results: house s02e07</span>&nbsp;Displaying hits from 1 to 6 (approx 6 found)</h2>
<br />
<div id="SearchResults"><div id="content">        <!-- right sky banner -->
        <div id="sky-right">
<script type="text/javascript">
pb_cid='BAYBANNER160X600_1';
pb_type='banner_160x600';
</script>
<script src="http://clkads.com/banners/script/include_img_banner.js" type="text/javascript"></script>

	</div>
<div id="main-content">
<!-- search ad -->
<script src="http://clkads.com/adServe/banners?tid=BAYBANNER728X90_2&size=728x90" type="text/javascript"></script>
<table id="searchResult">
	<thead id="tableHead">
		<tr class="header">
			<th><a href="/search/house%20s02e07/0/13/0" title="Order by Type">Type</a></th>
			<th><div class="sortby"><a href="/search/house%20s02e07/0/1/0" title="Order by Name">Name</a> (Order by: <a href="/search/house%20s02e07/0/3/0" title="Order by Uploaded">Uploaded</a>, <a href="/search/house%20s02e07/0/5/0" title="Order by Size">Size</a>, <span style="white-space: nowrap;"><a href="/search/house%20s02e07/0/11/0" title="Order by ULed by">ULed by</a></span>, <a href="/search/house%20s02e07/0/8/0" title="Order by Seeders">SE</a>, <a href="/search/house%20s02e07/0/9/0" title="Order by Leechers">LE</a>)</div><div class="viewswitch"> View: <a href="/switchview.php?view=s">Single</a> / Double&nbsp;</div></th>

			<th><abbr title="Seeders"><a href="/search/house%20s02e07/0/8/0" title="Order by Seeders">SE</a></abbr></th>
			<th><abbr title="Leechers"><a href="/search/house%20s02e07/0/9/0" title="Order by Leechers">LE</a></abbr></th>
		</tr>
	</thead>
	<tr>
		<td class="vertTh">
			<center>
				<a href="/browse/200" title="More from this category">Video</a><br />

				(<a href="/browse/205" title="More from this category">TV shows</a>)
			</center>
		</td>
		<td>
<div class="detName">			<a href="/torrent/4553044/Dirty_Sexy_Money_S02E07_The_Summer_House_HDTV_XviD-FQM_[eztv]" class="detLink" title="Details for Dirty Sexy Money S02E07 The Summer House HDTV XviD-FQM [eztv]">Dirty Sexy Money S02E07 The Summer House HDTV XviD-FQM [eztv]</a>
</div>
<a href="magnet:?xt=urn:btih:038afcbf064655596d0500af2b74ebddf731bd5d&dn=Dirty+Sexy+Money+S02E07+The+Summer+House+HDTV+XviD-FQM+%5Beztv%5D&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.istole.it%3A6969&tr=udp%3A%2F%2Ftracker.ccc.de%3A80" title="Download this torrent using magnet"><img src="static.thepiratebay.se/img/icon-magnet.gif" alt="Magnet link" /></a>			<a href="torrents.thepiratebay.se/4553044/Dirty_Sexy_Money_S02E07_The_Summer_House_HDTV_XviD-FQM_[eztv].4553044.TPB.torrent" title="Download this torrent"><img src="static.thepiratebay.se/img/dl.gif" class="dl" alt="Download" /></a><img src="static.thepiratebay.se/img/icon_comment.gif" alt="This torrent has 11 comments." title="This torrent has 11 comments." /><a href="/user/eztv"><img src="//static.thepiratebay.se/img/vip.gif" alt="VIP" title="VIP" style="width:11px;" border='0' /></a>
			<font class="detDesc">Uploaded 12-04&nbsp;2008, Size 349.95&nbsp;MiB, ULed by <a class="detDesc" href="/user/eztv/" title="Browse eztv">eztv</a></font>

		</td>
		<td align="right">7</td>
		<td align="right">1</td>
	</tr>
	<tr>
		<td class="vertTh">
			<center>
				<a href="/browse/200" title="More from this category">Video</a><br />

				(<a href="/browse/205" title="More from this category">TV shows</a>)
			</center>
		</td>
		<td>
<div class="detName">			<a href="/torrent/5511619/Celebrity.Rehab.Presents.Sober.House.S02E07.DSR.XviD-OMiCRON" class="detLink" title="Details for Celebrity.Rehab.Presents.Sober.House.S02E07.DSR.XviD-OMiCRON">Celebrity.Rehab.Presents.Sober.House.S02E07.DSR.XviD-OMiCRON</a>
</div>
<a href="magnet:?xt=urn:btih:48e104783930648f4107cb035ab438a0ab8efd56&dn=Celebrity.Rehab.Presents.Sober.House.S02E07.DSR.XviD-OMiCRON&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.istole.it%3A6969&tr=udp%3A%2F%2Ftracker.ccc.de%3A80" title="Download this torrent using magnet"><img src="static.thepiratebay.se/img/icon-magnet.gif" alt="Magnet link" /></a>			<a href="torrents.thepiratebay.se/5511619/Celebrity.Rehab.Presents.Sober.House.S02E07.DSR.XviD-OMiCRON.5511619.TPB.torrent" title="Download this torrent"><img src="static.thepiratebay.se/img/dl.gif" class="dl" alt="Download" /></a><img src="static.thepiratebay.se/img/icon_comment.gif" alt="This torrent has 3 comments." title="This torrent has 3 comments." /><a href="/user/TvTeam"><img src="//static.thepiratebay.se/img/vip.gif" alt="VIP" title="VIP" style="width:11px;" border='0' /></a>
			<font class="detDesc">Uploaded 04-24&nbsp;2010, Size 356.13&nbsp;MiB, ULed by <a class="detDesc" href="/user/TvTeam/" title="Browse TvTeam">TvTeam</a></font>

		</td>
		<td align="right">3</td>
		<td align="right">1</td>
	</tr>
	<tr>
		<td class="vertTh">
			<center>
				<a href="/browse/200" title="More from this category">Video</a><br />

				(<a href="/browse/205" title="More from this category">TV shows</a>)
			</center>
		</td>
		<td>
<div class="detName">			<a href="/torrent/3412776/House_S02E07_HDTV_XviD-LOL_[eztv]" class="detLink" title="Details for House S02E07 HDTV XviD-LOL [eztv]">House S02E07 HDTV XviD-LOL [eztv]</a>
</div>
<a href="magnet:?xt=urn:btih:8f02884b1641c97753b6cc00f4b4c95525b90463&dn=House+S02E07+HDTV+XviD-LOL+%5Beztv%5D&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.istole.it%3A6969&tr=udp%3A%2F%2Ftracker.ccc.de%3A80" title="Download this torrent using magnet"><img src="static.thepiratebay.se/img/icon-magnet.gif" alt="Magnet link" /></a>			<a href="torrents.thepiratebay.se/3412776/House_S02E07_HDTV_XviD-LOL_[eztv].3412776.TPB.torrent" title="Download this torrent"><img src="static.thepiratebay.se/img/dl.gif" class="dl" alt="Download" /></a><img src="static.thepiratebay.se/img/icon_comment.gif" alt="This torrent has 2 comments." title="This torrent has 2 comments." /><img src="static.thepiratebay.se/img/icon_image.gif" alt="This torrent has a cover image" title="This torrent has a cover image" /><a href="/user/eztv"><img src="static.thepiratebay.se/img/vip.gif" alt="VIP" title="VIP" style="width:11px;" border='0' /></a>
			<font class="detDesc">Uploaded 11-23&nbsp;2005, Size 350.69&nbsp;MiB, ULed by <a class="detDesc" href="/user/eztv/" title="Browse eztv">eztv</a></font>

		</td>
		<td align="right">3</td>
		<td align="right">1</td>
	</tr>
	<tr>
		<td class="vertTh">
			<center>
				<a href="/browse/200" title="More from this category">Video</a><br />

				(<a href="/browse/205" title="More from this category">TV shows</a>)
			</center>
		</td>
		<td>
<div class="detName">			<a href="/torrent/4553096/Dirty.Sexy.Money.S02E07.The.Summer.House.HDTV.XviD-FQM" class="detLink" title="Details for Dirty.Sexy.Money.S02E07.The.Summer.House.HDTV.XviD-FQM">Dirty.Sexy.Money.S02E07.The.Summer.House.HDTV.XviD-FQM</a>
</div>
<a href="magnet:?xt=urn:btih:29796f1ef5776997933437deac4b079c70239604&dn=Dirty.Sexy.Money.S02E07.The.Summer.House.HDTV.XviD-FQM&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.istole.it%3A6969&tr=udp%3A%2F%2Ftracker.ccc.de%3A80" title="Download this torrent using magnet"><img src="static.thepiratebay.se/img/icon-magnet.gif" alt="Magnet link" /></a>			<a href="torrents.thepiratebay.se/4553096/Dirty.Sexy.Money.S02E07.The.Summer.House.HDTV.XviD-FQM.4553096.TPB.torrent" title="Download this torrent"><img src="static.thepiratebay.se/img/dl.gif" class="dl" alt="Download" /></a><img src="static.thepiratebay.se/img/icon_comment.gif" alt="This torrent has 1 comments." title="This torrent has 1 comments." /><a href="/user/AiTB"><img src="//static.thepiratebay.se/img/vip.gif" alt="VIP" title="VIP" style="width:11px;" border='0' /></a>
			<font class="detDesc">Uploaded 12-04&nbsp;2008, Size 362.5&nbsp;MiB, ULed by <a class="detDesc" href="/user/AiTB/" title="Browse AiTB">AiTB</a></font>

		</td>
		<td align="right">0</td>
		<td align="right">1</td>
	</tr>
	<tr>
		<td class="vertTh">
			<center>
				<a href="/browse/200" title="More from this category">Video</a><br />

				(<a href="/browse/205" title="More from this category">TV shows</a>)
			</center>
		</td>
		<td>
<div class="detName">			<a href="/torrent/6555769/Help.My.House.Is.Falling.Down.S02E07.WS.PDTV.XviD-C4TV" class="detLink" title="Details for Help.My.House.Is.Falling.Down.S02E07.WS.PDTV.XviD-C4TV">Help.My.House.Is.Falling.Down.S02E07.WS.PDTV.XviD-C4TV</a>
</div>
<a href="magnet:?xt=urn:btih:5d47d79e67dc0f51f9a64c21c7fc4ca70fcead8d&dn=Help.My.House.Is.Falling.Down.S02E07.WS.PDTV.XviD-C4TV&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.istole.it%3A6969&tr=udp%3A%2F%2Ftracker.ccc.de%3A80" title="Download this torrent using magnet"><img src="static.thepiratebay.se/img/icon-magnet.gif" alt="Magnet link" /></a>			<a href="torrents.thepiratebay.se/6555769/Help.My.House.Is.Falling.Down.S02E07.WS.PDTV.XviD-C4TV.6555769.TPB.torrent" title="Download this torrent"><img src="static.thepiratebay.se/img/dl.gif" class="dl" alt="Download" /></a><a href="/user/scenebalance"><img src="static.thepiratebay.se/img/vip.gif" alt="VIP" title="VIP" style="width:11px;" border='0' /></a><img src="//static.thepiratebay.se/img/11x11p.png" />
			<font class="detDesc">Uploaded 07-21&nbsp;2011, Size 549.2&nbsp;MiB, ULed by <a class="detDesc" href="/user/scenebalance/" title="Browse scenebalance">scenebalance</a></font>

		</td>
		<td align="right">0</td>
		<td align="right">1</td>
	</tr>
	<tr>
		<td class="vertTh">
			<center>
				<a href="/browse/200" title="More from this category">Video</a><br />

				(<a href="/browse/205" title="More from this category">TV shows</a>)
			</center>
		</td>
		<td>
<div class="detName">			<a href="/torrent/6555777/Help.My.House.Is.Falling.Down.S02E07.WS.PDTV.XviD-C4TV" class="detLink" title="Details for Help.My.House.Is.Falling.Down.S02E07.WS.PDTV.XviD-C4TV">Help.My.House.Is.Falling.Down.S02E07.WS.PDTV.XviD-C4TV</a>
</div>
<a href="magnet:?xt=urn:btih:8b697da67e95c0ed9cf5179281a504f228329656&dn=Help.My.House.Is.Falling.Down.S02E07.WS.PDTV.XviD-C4TV&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.publicbt.com%3A80&tr=udp%3A%2F%2Ftracker.istole.it%3A6969&tr=udp%3A%2F%2Ftracker.ccc.de%3A80" title="Download this torrent using magnet"><img src="static.thepiratebay.se/img/icon-magnet.gif" alt="Magnet link" /></a>			<a href="torrents.thepiratebay.se/6555777/Help.My.House.Is.Falling.Down.S02E07.WS.PDTV.XviD-C4TV.6555777.TPB.torrent" title="Download this torrent"><img src="static.thepiratebay.se/img/dl.gif" class="dl" alt="Download" /></a><a href="/user/TvTeam"><img src="static.thepiratebay.se/img/vip.gif" alt="VIP" title="VIP" style="width:11px;" border='0' /></a><img src="//static.thepiratebay.se/img/11x11p.png" />
			<font class="detDesc">Uploaded 07-21&nbsp;2011, Size 549.19&nbsp;MiB, ULed by <a class="detDesc" href="/user/TvTeam/" title="Browse TvTeam">TvTeam</a></font>

		</td>
		<td align="right">0</td>
		<td align="right">2</td>
	</tr>

</table>
</div>
<div align="center"></div>	<!-- left sky -->
	<div class="ads" id="sky-banner">

<script type="text/javascript">
pb_cid='BAYBANNER120X600_1';
pb_type='banner_120x600';
</script>
<script src="http://clkads.com/banners/script/include_img_banner.js" type="text/javascript"></script>
	</div>
</div></div></div><!-- //div:content -->

	<div id="foot" style="text-align:center;margin-top:1em;">
<!-- bottom 728 -->
<script type="text/javascript">
pb_cid='BAYBANNER728X90_1';
pb_type='banner_728x90';
</script>
<script src="http://clkads.com/banners/script/include_img_banner.js" type="text/javascript"></script>
		<p>

			<a href="/login" title="Login">Login</a> | 
			<a href="/register" title="Register">Register</a> | 
			<a href="/language" title="Select language">Language / Select language</a> | 
			<a href="/about" title="About">About</a> | 
			<a href="/legal" title="Legal threats">Legal threats</a> | 
			<a href="/blog" title="Blog">Blog</a>

			<br />
			<a href="/contact" title="Contact us">Contact us</a> | 
			<a href="/policy" title="Usage policy">Usage policy</a> | 
			<a href="/downloads" title="Downloads">Downloads</a> | 
			<a href="/promo" title="Promo">Promo</a> | 
			<a href="/doodles" title="Doodles">Doodles</a> | 
			<a href="/searchcloud" title="Search Cloud">Search Cloud</a> | 
			<a href="/tags" title="Tag Cloud">Tag Cloud</a> | 
			<a href="http://suprbay.org/" title="Forum" target="_blank">Forum</a> | 
			<b><a href="http://www.bytelove.com" title="TPB T-shirts" target="_blank">TPB T-shirts</a></b>

			<br />
			<b><a href="http://bayfiles.com" title="Bayfiles" target="_blank">Bayfiles</a></b> | 
			<!-- <a href="http://baywords.com" title="BayWords" target="_blank">BayWords</a> | -->
			<a href="http://bayimg.com" title="BayImg" target="_blank">BayImg</a> | 
			<a href="http://www.pastebay.net" title="PasteBay" target="_blank">PasteBay</a> | 
			<!-- <a href="http://www.pirateshops.com" title="Pirate Shops" target="_blank">Pirate Shops</a> | -->
			<a href="https://www.ipredator.se" title="IPREDator" target="_blank">IPREDator</a> | 
			<a href="https://twitter.com/tpbdotorg" title="Twitter" target="_blank">Follow TPB on Twitter</a> | 
			<a href="https://www.facebook.com/ThePirateBayWarMachine" title="Facebook" target="_blank">Follow TPB on Facebook</a>

			<br />
		</p>

<p id="footer" style="color:#666; font-size:0.9em; ">
        5.712.255 registered users. Last updated 21:12:07.<br />
        30.065.851 peers (23.508.006 seeders + 6.557.845 leechers) in 3.829.630 torrents.<br />
</p>


		<div id="fbanners">

			<a href="/rss" class="rss" title="RSS"><img src="//static.thepiratebay.se/img/rss_small.gif" alt="RSS" /></a>
		</div><!-- // div:fbanners -->
	</div><!-- // div:foot -->
	<!-- popunder -->
<script type="text/javascript">
clicksor_enable_adhere = false;
clicksor_enable_pop = true; clicksor_frequencyCap = 12;
durl = '';
clicksor_default_url = '';
clicksor_banner_border = ; clicksor_banner_ad_bg = ;
clicksor_banner_link_color = ; clicksor_banner_text_color = ;
clicksor_layer_border_color = '';
clicksor_layer_ad_bg = ; clicksor_layer_ad_link_color = ;
clicksor_layer_ad_text_color = ; clicksor_text_link_bg = ;
clicksor_text_link_color = ''; clicksor_enable_text_link = false;
</script>
<script type="text/javascript" src="http://ads.clicksor.com/newServing/showAd.php?nid=1&amp;pid=233207&amp;adtype=&amp;sid=372720"></script>
<noscript><a href="http://www.yesadvertising.com">affiliate marketing</a></noscript>
</body>
</html>
"""
class TestTpbSearch(unittest.TestCase):
	""" Standard search testCase """
	def setUp(self): #pylint: disable=C0103
		""" setting Up, just creating the finder once"""
		self.finder = TPBMagnetFinder()

	def test_pattern(self):
		""" Simple pattern creation test"""
		sample_name = "Pouet S01E13.avi"
		self.assertTrue(self.finder.get_pattern(1, 13) in sample_name)
		self.assertFalse(self.finder.get_pattern(2, 13) in sample_name)

	def test_extraction(self):
		""" Test parsing a sample result HTML and verifying
		the extracted informations are corrects
		"""
		results = self.finder.extract_table_result(__sample_html__)
		self.assertTrue(results != None)
		self.assertTrue(len(results) == 6)
		#print("Found: {}\n".format(results[0].filename))
		#print("Found magnet: {}\n".format(results[0].magnet))
		wanted_name = "Dirty Sexy Money S02E07 The Summer House HDTV XviD-FQM [eztv]"
		wanted_magnet = "magnet:?xt=urn:btih:038afcbf064655596d0500af2\
b74ebddf731bd5d&dn=Dirty+Sexy+Money+S02E07+The+Summer+House+HDTV+XviD-FQM+%5Be\
ztv%5D&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A80&tr=udp%3A%2F%2Ftracker.p\
ublicbt.com%3A80&tr=udp%3A%2F%2Ftracker.istole.it%3A6969&tr=udp%3A%2F%2Ftracke\
r.ccc.de%3A80"
		self.assertTrue(results[0].filename == wanted_name)
		self.assertTrue(results[0].magnet == wanted_magnet)
		self.assertTrue(results[0].leechers == 7)

	def test_invalid_server(self):
		""" Test a ConnectionException """
		self.finder.server = "invalid.invalid"
		self.assertRaises(ConnectionException, self.request)
		#self.finder.get_candidates("plop",1,2)	
		
	def request(self):
		""" ??? Tests the entire process, with real 
		Connection to the server
		"""
		self.finder.get_candidates("plop", 1, 2)

