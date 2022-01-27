from WXBizDataCrypt import WXBizDataCrypt


def main():
    # appId = 'wx4f4bc4dec97d474b'
    # sessionKey = 'tiihtNczf5v6AKRyjwEUhQ=='
    # encryptedData = 'CiyLU1Aw2KjvrjMdj8YKliAjtP4gsMZMQmRzooG2xrDcvSnxIMXFufNstNGTyaGS9uT5geRa0W4oTOb1WT7fJlAC+oNPdbB+3hVbJSRgv+4lGOETKUQz6OYStslQ142dNCuabNPGBzlooOmB231qMM85d2/fV6ChevvXvQP8Hkue1poOFtnEtpyxVLW1zAo6/1Xx1COxFvrc2d7UL/lmHInNlxuacJXwu0fjpXfz/YqYzBIBzD6WUfTIF9GRHpOn/Hz7saL8xz+W//FRAUid1OksQaQx4CMs8LOddcQhULW4ucetDf96JcR3g0gfRK4PC7E/r7Z6xNrXd2UIeorGj5Ef7b1pJAYB6Y5anaHqZ9J6nKEBvB4DnNLIVWSgARns/8wR2SiRS7MNACwTyrGvt9ts8p12PKFdlqYTopNHR1Vf7XjfhQlVsAJdNiKdYmYVoKlaRv85IfVunYzO0IKXsyl7JCUjCpoG20f0a04COwfneQAGGwd5oa+T8yO5hzuyDb/XcxxmK01EpqOyuxINew=='
    # iv = 'r7BXXKkLb8qrSNn05n0qiA=='
    #
    # pc = WXBizDataCrypt(appId, sessionKey)
    #
    # print (pc.decrypt(encryptedData, iv))

    appId = 'wxafe035d3c21ea4ef'
    sessionKey = "/sRzMjOrYxDaZUXaC89KdQ=="
    # sessionKey = "nEBHeV8dnFuS2vuhhVO+cA=="
    encryptedData = "YxoJsz9MYHoFV+ktjBtpzLRWSztdoxbzaKR2rnsdyz0AZKIKf7lxx9BCz1ufGp+wqaXgWQGbBUBll+ChIi/OAOsoXOhwz7SoA8SlE2TNvt3DyG76I1v7wuPXwOewl8UUZAf6LjmRn2+5ODGp+9XXjYyNbEs14xlTrrfzVNL6hfXkyUz9aerXPR5N8lNQzdwrcVeJcF43Tc/MSztpvqQSLw9lZnqp9/5lqJRZkLywQ4nDy6dTdfiqBC3a+3It4gJmiNznaZjuZLmoEaawQhkEpm+b3wGeaclMkiwd27UqCFVaslst+fZLL+gHSEJjC6VbYs44j5++Tx/jBpcgO67ZLvTRBTq53CLkARKJZsJ9yCXVCvcjSDBojjAPu+NAd0yWe1kXFnTzubNsN9q2ErNYL+RARHRyWp6i0GhzrR7tRxk="
    iv = "9w+7LZXq3l0/QcQtGYYwnQ=="

    pc = WXBizDataCrypt(appId, sessionKey)

    print(pc.decrypt(encryptedData, iv))


if __name__ == '__main__':
    main()
