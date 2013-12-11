

function vote(q, v){

    var form = document.getElementById('voteform');
    var qt   = document.getElementById('votequestion');
    var vt   = document.getElementById('votedirection');

	
    if (form && qt && vt){
       qt.value = q;
       vt.value = v;
       form.submit();
    }

}