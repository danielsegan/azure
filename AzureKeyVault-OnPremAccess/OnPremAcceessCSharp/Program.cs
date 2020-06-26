using System;
using Microsoft.Azure.KeyVault;
using Microsoft.IdentityModel.Clients.ActiveDirectory;

using System.Threading.Tasks;

namespace OnPremAcceessCSharp
{
    class Program
    {    

        //https://docs.microsoft.com/en-us/azure/key-vault/general/tutorial-net-create-vault-azure-web-app
        static async Task Main(string[] args)
        {

            const string clientId = "";
            const string clientSecret = "";
            const string vaultUrl = @"";
            const string secretName = "";

            var kvClient = new KeyVaultClient(async (authority, resource, scope) =>
            {
                var context = new AuthenticationContext(authority);
                var credential = new ClientCredential(clientId, clientSecret);
                AuthenticationResult result = await context.AcquireTokenAsync(resource, credential);
                return result.AccessToken;
            });

            var secret = await kvClient.GetSecretAsync(vaultUrl, secretName);
            string secretValue = secret.Value;
            Console.WriteLine($"Hello World!: {secretValue}");
        }
    }
}
