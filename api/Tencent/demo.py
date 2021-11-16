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
    encryptedData = "HK4mvJ85GgNh4u/wAhmTOPSTtqU692rc0WUrNa4yw5k7Th1geVkHRlQGU/Rh4QKaxYdzwCxTKSq4tPuHB7OjALmPU50fSVGW4YMRlNl79oo1N2VWQ1CPfOw9zPJBN6Mt+naFgpsVEk8IKqVTvkkpZSmurwerULrmM3PJF4rJqAMK0OAm9bcIrTAzUPY6CAXmDGxuZsaHFyg7cHO1JjbsUiAM06ZEuz89vR1A25MprjAAeYGzxUVxeGeO4ZHEJVUwbUWFWgEGwQGbNM4wiLSG2He32NmlJWsNDPdFd+UPIBFU/9ZrcniLtbWPj+0n1Z+L+bGwySSPWkUwnu1iB+Xop70oyd4Dseb4AN23u4VPLsPxTDqciq9a6hUoEbFKyNjXbDeZlXOLavvatzYN6CoNqw=="
    iv = "/QZiPfM+/m5qBeAihqezhw=="

    pc = WXBizDataCrypt(appId, sessionKey)

    print(pc.decrypt(encryptedData, iv))


if __name__ == '__main__':
    main()
