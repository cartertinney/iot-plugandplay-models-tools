﻿using Microsoft.Azure.DigitalTwins.Parser;
using System;
using System.Diagnostics;
using System.Reflection;

namespace Azure.Iot.ModelsRepository.CLI
{
    internal class Outputs
    {
        public static readonly string ParserVersion = FileVersionInfo.GetVersionInfo(typeof(ModelParser).Assembly.Location).ProductVersion;
        public static readonly string ResolverVersion = FileVersionInfo.GetVersionInfo(typeof(ResolverClient).Assembly.Location).ProductVersion;
        public static readonly string CliVersion = FileVersionInfo.GetVersionInfo(Assembly.GetExecutingAssembly().Location).ProductVersion;
        public static readonly string StandardHeader = $"dmr-client/{CliVersion} parser/{ParserVersion} resolver/{ResolverVersion}";

        public static void WriteError(string msg)
        {
            Console.ForegroundColor = ConsoleColor.Red;
            Console.Error.WriteLine($"Error: {msg}");
            Console.ResetColor();
        }

        public static void WriteHeader()
        {
            Console.ForegroundColor = ConsoleColor.Green;
            Console.Error.WriteLine(StandardHeader);
            Console.ResetColor();
        }

        public static void WriteOut(string content, ConsoleColor? color=null)
        {
            if (color.HasValue)
            {
                Console.ForegroundColor = color.Value;
            }

            Console.Out.WriteLine(content);

            if (color.HasValue)
            {
                Console.ResetColor();
            }
        }

        public static void WriteDebug(string debug, ConsoleColor? color = null)
        {
            if (!color.HasValue)
            {
                Console.ForegroundColor = ConsoleColor.DarkCyan;
            }

            Console.Error.WriteLine(debug);
            Console.ResetColor();
        }
    }
}
