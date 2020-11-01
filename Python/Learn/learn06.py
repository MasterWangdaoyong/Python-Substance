#20200918  6.4 嵌套
# favorite_languages = {
#     'jen' : ['python', 'ruby'],
#     'sarah' : ['c'],
#     'edward' : ['ruby', 'go'],
#     'phil' : ['python', 'haskell'],
# }  
# for name, languages in favorite_languages.items():
#     print('\n' + name.title() + 's favorite languages are:')
#     for language in languages:
#         print('\t' + language.title())

#6.4.3  在字典中存储字典
user = {
    'aeinstein' : {
        'first' : "albert",
        'last' : 'einstein',
        'location' : 'princeton',
    },

    'mcurie' : {
        'first' : 'marie',
        'last' : 'curie',
        'location' : 'paris',
    },
}

for username, user_info in user.items():
    print('\nUsername: ' + username)
    full_name = user_info['first'] + " " + user_info['last']
    location = user_info['location']

    print('\tFull name: ' + full_name.title())
    print('\tLocation: ' + location.title())
    