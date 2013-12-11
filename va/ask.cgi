#!/usr/bin/perl -Tw

####################################333
# Election application
# Written by Jørgen Elgaard Larsen
# HTML and design by Ole Tange
# Licensed under the GNU GPL version 3.



use CGI;
use DBI;


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

my $uid = int $q->param('uid');


if (not $q->param('asked')){
    
    ## Show form
    
    $page .= qq|
	<form action="ask.cgi" method="post">
	<input type="hidden" name="asked" value="question" />
	<input type="hidden" name="template" value="${template}" />
	<input type="hidden" name="uid" value="${uid}" />
	<h2>Stil spørgsmål:</h2>
	<textarea cols="60" rows="7" name="my_question"></textarea>
	<br/>
	<input type="submit" onclick="return(confirm('Er du sikker på, at du vil sende dette spørgsmål?'))" name="sendin" value="Afsend" />
	</form>
	|;

} else {
    ## Register question

    my $content = $q->param('my_question') || '';

    # Trim
    $content =~ s/(^\s+)|(\s+$)//g;

    # Escape html tags
    $content =~ s/</&lt;/g;
    $content =~ s/>/&gt;/g;

    if ($content){
	my $dbh = DBI->connect('dbi:mysql:host=localhost;database=valg', 'valg', 'secret', {});
	
	unless ($dbh){
	    $page .= qq|<p class="error">No database connection</p>|;
	}

	$dbh->do("INSERT INTO question (content, askedby) VALUES (?, ?)", undef, $content, $ENV{REMOTE_ADDR});
	# Get inserted ID
	my $qid = 0;
	my $sth= $dbh->prepare("select LAST_INSERT_ID()");
	if ($sth){
	    $sth->execute();
	    ($qid) = $sth->fetchrow_array;
	    $sth->finish;
	}
	$dbh->do("INSERT INTO votes (question, uid, vote) VALUES (?, ?, 1)", undef, $qid, $uid);
	$page .= qq|<p>Tak for dit spørgsmål. Det er nu registreret.</p>|;
    } else {
	$page .= qq|<p class="error">Du skrev ikke noget i dit spørgsmål!</p>|;
    }

			  
}


$page .= qq|<p><a href="javascript:window.close()" class="close">Luk vinduet</a></p>|;



print "Content-Type: text/html\n\n";
$skab =~ s/<!--HEADER-->/$header/g;
$skab =~ s/<!--CONTENT-->/$page/g;

print $skab;



exit;

