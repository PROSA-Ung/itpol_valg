#!/usr/bin/perl -Tw

####################################333
# Election application
# Written by Jørgen Elgaard Larsen
# HTML and design by Ole Tange
# Licensed under the GNU GPL version 3.

use utf8::all;

use CGI;
use DBI;


my %admins = (
	      $ENV{'ADMIN_UID'} => 1,
	      );


my $q = new CGI;

# Read and clean template
my $template = $q->param('template') || '';
$template =~ s/[^a-zA-Z0-9]//g;

# Default template
unless ($template){
    $template='skabelon';
}

# Get template
my $skab = '<html><head><!--HEADER--></head><body><!--CONTENT--></body></html>';
if (open SKAB, "<${template}.html"){
    $skab = join "", <SKAB>;
    close SKAB;
}

my $page = '';
my $header = '';

my $dbh = DBI->connect("dbi:mysql:host=$ENV{'DB_HOST'};database=$ENV{'DB_NAME'}", "$ENV{'DB_USER'}", "$ENV{'DB_PASS'}", {mysql_enable_utf8 => 1});

unless ($dbh){
    $page .= qq|<p class="error">No database connection</p>|;
}

# Get mode and sort
my $mode = $q->param('mode') || '';
my $sort = $q->param('sort') || '';


# Get uid
my $uid = int ($q->param('force_uid') || $q->cookie('uid') || $q->param('uid') || 0);
unless ($uid){
    if ($mode eq 'novote'){
	$uid = 3;
    } else {

	# Insert new user
	$dbh->do("INSERT INTO user (ip) VALUES (?)", undef, $ENV{REMOTE_ADDR});
	
	# Get inserted ID
	my $sth= $dbh->prepare("select LAST_INSERT_ID()");
	if ($sth){
	    $sth->execute();
	    ($uid) = $sth->fetchrow_array;
	    $sth->finish;
	}
    }
}


my $isadmin = $admins{$uid} || 0;


# Slet evt. spm.
if ($isadmin and ($q->param('delete_question') or $q->param('answer_question'))){
    my $qid = int $q->param('answer_question') || $q->param('delete_question');
    if ($q->param('answer_question')){	
	$dbh->do("UPDATE question SET deleted=1, answered = NOW() WHERE id = ?", undef, $qid);
    } else {
	$dbh->do("UPDATE question SET deleted=1 WHERE id = ?", undef, $qid);
    }
}



# Get refresh
my $refresh;

if (defined $q->param('refresh')){
    $refresh = int $q->param('refresh');
} else {
    $refresh = 120;
}
if ($refresh and $refresh < 10){
    $refresh = 10;
}

# Calculate continuence string
my $params = qq|<input type="hidden" name="uid" value="$uid"/>
                <input type="hidden" name="mode" value="$mode"/>
                <input type="hidden" name="template" value="$template"/>
                <input type="hidden" name="refresh" value="$refresh" id="refresh"/>
    <input type="hidden" name="sort" value="$sort"/>|;
my $gparams = qq|uid=$uid&amp;mode=$mode&amp;refresh=$refresh&amp;template=$template|;



# Vote
if ($q->param('votequestion')){
    my $p = 0;
    if ($q->param('votedirection') eq 'up'){
	$p = 1;
    } elsif ($q->param('votedirection') eq 'down'){
	$p = -1;
    }
    my $qid = $q->param('votequestion');

    $dbh->do("DELETE FROM votes WHERE question = ? AND uid = ?", undef, $qid, $uid);
    $dbh->do("INSERT INTO votes (question, uid, vote) VALUES (?,?,?)", undef, $qid, $uid, $p);
}


# Make hidden form
$page .= qq|<form action="index.cgi" method="post" id="voteform">
              $params
	      <input type="hidden" name="votequestion" id="votequestion" value=""/>
	      <input type="hidden" name="votedirection" id="votedirection" value=""/>
	    </form>
	    |;

my $numberoffer = 'id_down';
my $pointsoffer = 'points_down';
if ($sort eq 'points_down'){
    $pointsoffer = 'points_up';
}
if ($sort eq 'id_down'){
    $numberoffer = 'id_up';
}

# Table start
$page .= qq|
  <table border="0" class="questiontable">
   <tr>
    |;
if ($mode ne 'novote'){
    $page .= qq|<th class="number"><a href="index.cgi?$gparams&amp;sort=$numberoffer">Nummer</a></th>|;
}
$page .= qq|
    <th class="question">Spørgsmål</th>
    <th class="points"><a href="index.cgi?$gparams&amp;sort=$pointsoffer">Points</a></th>
    |;
if ($mode ne 'novote'){
    $page .= qq|
	<th class="vote">Stem</th>
	|;
}
if ($isadmin and $mode ne 'novote'){
    $page .= qq|
	<th>&nbsp;</th>
	|;
   
}

$page .= qq|
   </tr>
  |;


# Loop over questions
my $rowno = 0;

my $order = 'total desc, q.id asc';
if ($sort eq 'points_up'){
    $order = 'total asc, q.id asc';
} elsif ($sort eq 'id_up'){
    $order = 'q.id asc, total asc';
} elsif ($sort eq 'id_down'){
    $order = 'q.id desc, total desc';
}

my $sth = $dbh->prepare(" select *, votes.vote as mine from
                             ( select id, content, edited, sum(vote) as total
                                  from question left outer join votes on 
                                  (votes.question = question.id)
                                where question.deleted = 0   
                                group by question.id, content, edited
                             ) as q
                            left outer join votes on (votes.uid = ?
                              and votes.question = q.id)
                            order by $order");

if ($sth){
    $sth->execute($uid);

    while (my $row = $sth->fetchrow_hashref){
	$rowno++;
	my $content = $row->{content};
	$content = $row->{edited} || $content;
	my $total = int $row->{total};
	my $class = ($rowno % 2)?'odd':'even';
	
	$page .= qq|<tr class="$class">\n|;
	if ($mode ne 'novote'){
	    $page .= qq|<td class="number">$row->{id}</td>\n|;
	}
	$page .= qq|<td class="question">$content</td>
	    <td class="points">$total</td>
	    |;

	if ($mode ne 'novote'){
	    my $mine = int ($row->{mine} || 0);
	    
	    # Make voting buttons
	    my %check = (
			 up   => ($mine > 0)?'checked="checked"':'',
			 stay => ($mine == 0)?'checked="checked"':'',
			 down => ($mine < 0)?'checked="checked"':'',
			 );
	    
	    my %onclick = (
			   up   => ($mine > 0)?'':qq|onclick="vote($row->{id},'up')"|,
			   stay => ($mine == 0)?'':qq|onclick="vote($row->{id},'neutral')"|,
			   down => ($mine < 0)?'':qq|onclick="vote($row->{id},'down')"|,
			   );
	    
	    
	    $page .= qq|<td class="vote">
		<input type="radio" name="vote_$row->{id}" value="up" $check{up} $onclick{up}/><b>+</b><br/>
		<input type="radio" name="vote_$row->{id}" value="stay" $check{stay} $onclick{stay}/><b>?</b><br/>
		<input type="radio" name="vote_$row->{id}" value="down" $check{down} $onclick{down}/><b>-</b>
		</td>|;
	}

	if ($isadmin and $mode ne 'novote'){
	    $page .= qq(
		<td class="admincell">
		  <a href="index.cgi?answer_question=$row->{id}&amp;${gparams}&amp;sort=$sort&amp;refresh=${refresh}"
                     onclick="return(confirm('Er du sikker på, at du vil markere Spørgsmål $row->{id} som besvaret?'))">Besvaret</a>
		     | <a href="moderate.cgi?qid=$row->{id}&amp;${gparams}" target="_blank">Moderær</a>
		     | <a href="index.cgi?delete_question=$row->{id}&amp;${gparams}&amp;refresh=${refresh}&amp;sort=$sort"
                     onclick="return(confirm('Er du sikker på, at du vil slette Spørgsmål $row->{id} ?'))">Slet</a>
		</td>
		);
	}

	$page .= qq|</tr>\n|;

    }

} else {
    $page .= qq|<p class="error">Could not get questions: $DBI::errstr </p>|;
}




$page .= qq|</table><br/>
            <form action="index.cgi" method="post" id="refreshform">
              <input type="hidden" name="uid" value="$uid"/>
              <input type="hidden" name="mode" value="$mode"/>
              Opdater hvert <input type="text" name="refresh" value="$refresh" size="4"/> sekund (0 for ingen opdatering)<br/>
              <input type="submit" value="ok"/>
	    </form>
           |;



if ($mode ne 'novote'){
    $page .= qq|<p><a href="ask.cgi?$uid=${uid}&amp;template=question" target="_blank" class="asklink">Stil nyt Spørgsmål</a></p>|;
}

$header .= qq|<script type="text/javascript" src="lib.js" ></script>\n|;

if ($refresh){
    $header .= qq|<meta http-equiv="refresh" content="$refresh;index.cgi?$gparams&amp;sort=$sort"/>\n|;
}



my $cookie = $q->cookie(-name=>'uid',
			-value=>$uid,
			-expires=>'+1d',
			-path=>'/va',
			-domain=>'valg.itpol.dk',
			-secure=>0);
print $q->header(-type  => 'text/html',
		 -charset => 'UTF-8',       
		 -cookie=>$cookie);


$skab =~ s/<!--HEADER-->/$header/g;
$skab =~ s/<!--CONTENT-->/$page/g;

print $skab;


exit;

