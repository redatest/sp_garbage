base_sidecontent.html is needed in all template files

index.html 				only base_sidecontent.html

contact.html 			simple_sidecontent.html

news.html 				simple_sidecontent.html  --> needs some refactoring to be just for no logged in users

candid_profile 			no side content page

candid_profile_edit 	no side content page

candid_profile_marks 	no side content page


when candidate is logged in:
/search : 			search_sidecontent.html
/map_search : 		search_sidecontent.html


when employer is logged in:
/deposer_offer: 	search_sidecontent_emp.html
/search_emp : 		search_sidecontent_emp.html
/map_search_emp : 	search_sidecontent_emp.html
/emp_profile : 		no other side content page




{% include "./parts/tabbed_posts.html" %}

{% include "./parts/stayintouch.html" %}


also . decompose searching forms for both employer and candidate

make favorite candid offers with different colours