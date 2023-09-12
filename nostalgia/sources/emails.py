# pdir(e)
# e.as_string()
# e.values()
# e.get_payload()
# e.get_payload()[0]
# pdir(e.get_payload()[0])
# e.get_payload()[0].get_payload()
# e.get_payload()[1].get_payload()
# import lxml.html
# lxml.html.fromstring(e.get_payload()[1].get_payload())
# html = lxml.html.fromstring(e.get_payload()[1].get_payload())
# from requests_viewer import view_html
# view_html(html)
# view_tree(html)
# from requests_viewer import view_tree
# view_tree(html)
# html.text_content()
# print(html.text_content())
# from auto_extract import parse_article
# parse_article(html)
# from auto_extract import Article
# Article
# ?Article
# help(Article)
# a = Article(e.get_payload()[1].get_payload(), "")
# a
# a.content
# a.body
# pdir(a)
# a.article_text
# a.full_text
# import justtext
# import justext
# pdir(justext)
# justext.justext(e.get_payload()[1].get_payload())
# justext.justext(e.get_payload()[1].get_payload(), [])
# justext.justext(e.get_payload()[1].get_payload(), [])[0]
# pdir(justext.justext(e.get_payload()[1].get_payload(), [])[0])
# [x.text for x in justext.justext(e.get_payload()[1].get_payload(), [])]
# [x.text for x in justext.justext(e.get_payload()[1].get_payload(), []) if not x.is_boilerplate]
# [x.text for x in justext.justext(e.get_payload()[1].get_payload(), []) if not x.is_boilerplate]
# [x.text for x in justext.justext(e.get_payload()[1].get_payload(), []) if not x.is_boilerplate]
# [x.text for x in justext.justext(e.get_payload()[1].get_payload(), []) if not x.is_boilerplate and x.is_heading]
# [x.text for x in justext.justext(e.get_payload()[1].get_payload(), []) if not x.is_boilerplate or x.is_heading]
# import just
# import email
# e=email.message_from_string(just.read("/home/pascal/.mail/outlook/Inbox/new/1582889346_0.7224.archbook,U=38807,FMD5=3882d32c66e7e768145ecd8f104b0c08:2,",unknown_type="txt"))
# [x.text for x in justext.justext(e.get_payload()[1].get_payload(), []) if not x.is_boilerplate or x.is_heading]
# [x.text for x in justext.justext(e.get_payload()[1].get_payload(), [])]
# [x.text for x in justext.justext(e.get_payload()[1].get_payload(), [])]
# e.get_payload()[1].get_payload()
# view_html(e.get_payload()[1].get_payload())
