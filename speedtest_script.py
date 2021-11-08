class Solution(object):

    def longestPalindrome(self, s):
        """
        :type s: str
        :rtype: str
        """
        max_len = 0
        result = ""
        if len(s) == 1:
            return s

        for idx, i in enumerate(s):
            dif = self.check_odd(s, idx, 1)
            total_len = 2 * dif + 1
            if (total_len > max_len):
                max_len = total_len
                result = s[idx - dif:idx + dif + 1]
        for idx, i in enumerate(s):
            if idx == 0:
                continue
            print(idx)
            dif = self.check_even(s, idx - 1, idx, 0)
            print(dif)
            total_len = 2 * dif + 2
            if (total_len > max_len):
                max_len = total_len
                result = s[idx - dif - 1:idx + dif + 1]
            # if max_len == 0:
            #     return s[0]

        return result

    def check_odd(self, s, idx, i):
        if idx - i < 0 or idx + i >= len(s):
            return 0
        if s[idx - i] == s[idx + i]:
            return 1 + self.check_odd(s, idx, i + 1)
        else:
            return 0

    def check_even(self, s, left, right, i):
        print(left)
        print(right)
        if left - i < 0 or right + i >= len(s):
            return i - 1
        if s[left - i] == s[right + i]:
            print("in")
            return self.check_even(s, left, right, i + 1)
        else:
            return i - 1


x = Solution()
print(x.longestPalindrome("abb"))

   
