﻿using System.IO;
using System.Text.RegularExpressions;
using Azure.DigitalTwins.Validator.Exceptions;

namespace Azure.DigitalTwins.Validator
{
    public static partial class Validations
    {
        public static bool ValidateFilePath(this FileInfo fileInfo)
        {
            return ValidateFilePath(fileInfo.FullName);
        }

        public static bool ValidateFilePath(string fullPath)
        {
            var filePathRegex = new Regex("dtmi[\\\\\\/](?:_+[a-z0-9]|[a-z])(?:[a-z0-9_]*[a-z0-9])?(?:[\\\\\\/](?:_+[a-z0-9]|[a-z])(?:[a-z0-9_]*[a-z0-9])?)*-[1-9][0-9]{0,8}\\.json$");

            if (!filePathRegex.IsMatch(fullPath))
            {
                throw new FilePathValidationException(fullPath);
            }
            return true;
        }
    }
}