#!/usr/bin/env python3

import sys
import random
import proxy
from socket import socket
import unittest
import glob

class TestYourModule(unittest.TestCase):

    def test_parsingTestsWIthoutPort(self):
        sampleUri = "GET http://catb.org/~esr/jargon/ HTTP/1.0"
        results = proxy.parseUri(sampleUri)
        self.assertEqual(results.port, 80)
        self.assertEqual(results.host,"catb.org")
        self.assertEqual(results.path,"/~esr/jargon/")
        self.assertEqual(results.fullPath,"http://catb.org/~esr/jargon/")

    def test_parstingTestWithPort(self):
        sampleUri = "GET http://www.example.com:8080/path/ HTTP/1.0"
        results = proxy.parseUri(sampleUri)
        self.assertEqual(results.port, 8080)
        self.assertEqual(results.host,"www.example.com")
        self.assertEqual(results.path,"/path/")
        self.assertEqual(results.fullPath, "http://www.example.com:8080/path/")

    def test_parstingTestWithoutPath(self):
        sampleUri = "GET http://www.example.com/ HTTP/1.0"
        results = proxy.parseUri(sampleUri)
        self.assertEqual(results.host,"www.example.com")
        self.assertEqual(results.path,"/")
        self.assertEqual(results.fullPath, "http://www.example.com/")

    def test_keyValuePairs(self):
        i = 0
        listOfPairs = []
        while i < 5:
            listOfPairs.append(f"Key{i}:Value{i}")
            i += 1
        hostMentioned, result = proxy.readKeyValuePairs(listOfPairs)
        self.assertIsNot(result, "")
        assert "0" not in result
        print(result)

    def test_keyValuePairsWithHost(self):
        i = 0
        listOfPairs = []
        while i < 5:
            listOfPairs.append(f"Host{i}:Value{i}")
            i += 1
        hostMentioned, result = proxy.readKeyValuePairs(listOfPairs)
        self.assertIsNot(result, "")
        self.assertEqual(hostMentioned, True)
        print(result)

    def test_cache(self):
        proxy.cacheUrl("http://tired.com/", "success".encode())
        result = proxy.checkCacheAndReturnCachedIfPresent("http://tired.com/")
        self.assertNotEquals("", result)

### main ###
if __name__=="__main__":
    unittest.main()